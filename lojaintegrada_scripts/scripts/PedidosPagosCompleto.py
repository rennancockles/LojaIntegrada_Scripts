# -*- coding: utf-8 -*-

import logging
import xlsxwriter
from datetime import date
from os import path

from pagamentos import Pagamento
from plataformas import PlataformaABC
from helpers import add_util_days, to_money, mailer

logger = logging.getLogger(__name__)
CWD = path.dirname(path.abspath(__file__))
TMP = path.join(CWD, '..', 'tmp')

class PedidosPagosCompleto:
  def __init__(self, plataforma:PlataformaABC, datas:list[date], email_to:list):
    self.plataforma = plataforma
    self.datas = datas
    self.email_to=email_to

  def __call__(self):
    logger.info(f'buscando atualizacoes entre {self.datas[0]} e {self.datas[-1]}')
    atualizacoes = self.plataforma.lista_atualizacoes_por_datas(self.datas)
    logger.info('atualizacoes obtidas com sucesso')

    pedidos = []
      
    for data in self.datas:
      logger.info(f'executando para a data {data}')
      atualizacoes_pedidos_pagos = atualizacoes.get(str(data), {}).get('pedido_pago', [])

      pedidos += self.get_pedidos(atualizacoes_pedidos_pagos, data)

    if pedidos:
      # csv_path = to_csv(pedidos)
      xlsx_path = self.to_excel(pedidos)
      self.send_mail(xlsx_path)

  def get_pedidos(self, atualizacoes_pedidos_pagos, data:date):
    logger.info(f'{len(atualizacoes_pedidos_pagos)} pedidos pagos')
    pedidos = []
    total = 0

    for atualizacao in atualizacoes_pedidos_pagos:
      pedido = self.plataforma.get_pedido_info(atualizacao['numero'])
      total += float(pedido['valor_total']) 
      pedido['data_leitura'] = data
      pedido['detalhe_pagamento'] = Pagamento.consulta_detalhe_transacao(forma_pagamento=pedido['pagamentos'][0]['forma_pagamento']['codigo'], transacao_id=pedido['pagamentos'][0]['transacao_id'])
      logger.debug(f"Pedido {pedido['numero']} => {to_money(pedido['valor_total'])}")
      pedidos.append(self.pedido_mapper(pedido))
    
    logger.info(f"Total {to_money(total)}")
    return pedidos

  def pedido_mapper(self, pedido):
    cliente = pedido['cliente']
    envio = pedido['envios'][0]
    pagamento = pedido['pagamentos'][0]
    detalhe_pagamento = pedido['detalhe_pagamento']
    itens = pedido['itens']

    disponibilidade = max(map(lambda item: int(item['disponibilidade']), pedido['itens']))
    custo = sum(map(lambda item: float(item['preco_custo']), pedido['itens']))

    cupom = ''
    if pedido['cupom_desconto'] is not None:
      cupom = pedido['cupom_desconto'].get('codigo', '')

    total_liquido = detalhe_pagamento.get('total_liquido', '')
    lucro_bruto = ''
    if total_liquido:
      total_liquido = float(total_liquido)
      lucro_bruto = total_liquido - custo

    return {
      'Data': pedido['data_leitura'].strftime('%d/%m/%Y'),
      'Cliente': cliente['nome'],
      'Pedido': pedido['numero'],
      'Prazo de Envio': add_util_days(pedido['data_leitura'], disponibilidade).strftime('%d/%m/%Y'),

      'Itens': [{
        'SKU': it['sku'], 
        'Itens': it['nome'], 
        'QTD': float(it['quantidade']),
        'Fornecedor': '',
        'Custo Real': '',
        'Custo Site': to_money(it['preco_custo']),
        'Preço Vendido': to_money(it['preco_venda'])} 
        for it in itens],

      'Situação': pedido['situacao']['nome'],
      'Liberação do Pagamento': detalhe_pagamento.get('liberacao_pagamento', ''),

      'Pagamento': f"{pagamento['forma_pagamento']['codigo']} - {pagamento['forma_pagamento']['nome']}",
      'Código': pagamento['transacao_id'],
      'Parcelas': pagamento['parcelamento'].get('numero_parcelas', 0),
      'Cupom': cupom,

      'Data Envio': '',
      'Rastreio': envio['objeto'],
      'Frete Real': '',

      # 'Disponibilidade': disponibilidade,
      'Prazo de Frete': int(envio['prazo']) - disponibilidade,
      'Envio': f"{envio['forma_envio']['nome']} - {envio['forma_envio']['tipo']}",
      'CEP': pedido['endereco_entrega']['cep'],
      'Estado': pedido['endereco_entrega']['estado'],

      'Subtotal': to_money(pedido['valor_subtotal']),
      'Desconto': to_money(pedido['valor_desconto']),
      'Frete': to_money(pedido['valor_envio']),
      'Total': to_money(pedido['valor_total']),
      'Taxas': to_money(detalhe_pagamento.get('taxas', '')),
      'Total Líquido': to_money(total_liquido),    
      # 'Lucro Bruto': to_money(lucro_bruto),
    }

  def send_mail(self, file_path:str):
    logger.info("Enviando email")
    if not self.email_to:
      logger.error("Email não enviado")
      return

    br_date_i = self.datas[0].strftime('%d/%m/%Y')
    br_date_f = self.datas[-1].strftime('%d/%m/%Y')

    subject = f"Dados do dia {br_date_i}"
    body = f'Bom dia \n\nsegue em anexo os pedidos pagos do dia {br_date_i}'
    files_to_send=[{'name': 'Pedidos Pagos', 'file': file_path}]

    if self.datas[0] != self.datas[-1]:
      subject += f" ao dia {br_date_f}"
      body += f' ao dia {br_date_f}'

    mailer.send(email_to=self.email_to,
                subject=subject,
                body=body,
                files_to_send=files_to_send)
    logger.info("Email enviado com sucesso!")

  def to_excel(self, pedidos):
    file_path = path.join(TMP, 'tmp.xlsx')
    workbook = xlsxwriter.Workbook(file_path)
    worksheet = workbook.add_worksheet()
    row = 1

    self._write_excel_header(workbook, worksheet, pedidos)

    for pedido in pedidos:
      itens_length = len(pedido.get('Itens', [0]))
      self._write_excel_row(workbook, worksheet, row, row + itens_length - 1, pedido)
      row += itens_length

    workbook.close()
    return file_path

  def _write_excel_row(self, workbook, worksheet, first_row, last_row, row_data):
    col = -1
    body_format = workbook.add_format({
      'font_size': 9,
      'align': 'center',
      'valign': 'vcenter',
    })

    for _, value in row_data.items():
      col += 1
      if type(value) == list:
        for i, list_item in enumerate(value):
          sub_col = col - 1
          for item in list_item.values():
            sub_col += 1
            worksheet.write(first_row + i, sub_col, item, body_format)
        col = sub_col
      else:
        if first_row == last_row: 
          worksheet.write(first_row, col, value, body_format)
        else:
          worksheet.merge_range(first_row, col, last_row, col, value, body_format)

  def _write_excel_header(self, workbook, worksheet, row_data):
    header_format = workbook.add_format({
      'bold': True,
      'font_size': 9,
      'bg_color': '#b7e1cd',
      'align': 'center',
      'valign': 'vcenter',
    })

    row = 0
    headers = []
    for k, v in row_data[0].items():
      headers += v[0].keys() if type(v) == list else [k]

    for i, header in enumerate(headers):
      worksheet.write(row, i, header, header_format)