# -*- coding: utf-8 -*-

import logging
import os
from datetime import datetime, date

from lojaintegrada import LojaIntegrada
from pagseguro import PagSeguro
from helpers import add_util_days, to_money, to_csv, mailer

logger = logging.getLogger(__name__)

class PedidosPagos:
  def __init__(self, LI:LojaIntegrada, datas:list[date], email_to:list):
    self.pagseguro = PagSeguro(email=os.getenv("PAGSEGURO_EMAIL"), token=os.getenv("PAGSEGURO_TOKEN"))

    self.ecommerceAPI = LI
    self.datas = datas
    self.email_to=email_to

  def __call__(self):
    logger.info(f'buscando atualizacoes entre {self.datas[0]} e {self.datas[-1]}')
    atualizacoes = self.ecommerceAPI.lista_atualizacoes_por_datas(self.datas)
    logger.info('atualizacoes obtidas com sucesso')

    pedidos = []
      
    for data in self.datas:
      logger.info(f'executando para a data {data}')
      atualizacoes_pedidos_pagos = atualizacoes.get(str(data), {}).get('pedido_pago', [])

      pedidos += self.get_pedidos(atualizacoes_pedidos_pagos, data)

    if pedidos:
      csv_path = to_csv(pedidos)
      self.send_mail(csv_path)

  def get_pedidos(self, atualizacoes_pedidos_pagos, data:date):
    logger.info(f'{len(atualizacoes_pedidos_pagos)} pedidos pagos')
    pedidos = []
    total = 0

    for atualizacao in atualizacoes_pedidos_pagos:
      pedido = self.ecommerceAPI.get_pedido_info(atualizacao['numero'])
      total += float(pedido['valor_total']) 
      pedido['data_leitura'] = data
      pedido['detalhe_pagamento'] = {}
      logger.debug(f"Pedido {pedido['numero']} => {to_money(pedido['valor_total'])}")
      
      if pedido['pagamentos'][0]['transacao_id']:
        pedido['detalhe_pagamento'] = self.pagseguro.consulta_detalhe_transacao(pedido['pagamentos'][0]['transacao_id'])

      pedidos.append(self.pedido_mapper(pedido))
    
    logger.info(f"Total {to_money(total)}")
    return pedidos

  def pedido_mapper(self, pedido):
    cliente = pedido['cliente']
    envio = pedido['envios'][0]
    pagamento = pedido['pagamentos'][0]
    detalhe_pagamento = pedido['detalhe_pagamento'].get('transaction', {})

    disponibilidade = max(map(lambda item: int(item['disponibilidade']), pedido['itens']))
    custo = sum(map(lambda item: float(item['preco_custo']), pedido['itens']))

    cupom = ''
    if pedido['cupom_desconto'] is not None:
      cupom = pedido['cupom_desconto'].get('codigo', '')

    total_liquido = detalhe_pagamento.get('netAmount', '')
    lucro_bruto = ''
    if total_liquido:
      total_liquido = float(total_liquido)
      lucro_bruto = total_liquido - custo

    liberacao_pagamento = detalhe_pagamento.get('escrowEndDate', '')
    if liberacao_pagamento:
      liberacao_pagamento = datetime.strptime(liberacao_pagamento.split('T')[0], "%Y-%m-%d").strftime('%d/%m/%Y')

    return {
      'cliente': cliente['nome'],
      'pedido': pedido['numero'],
      'situação': pedido['situacao']['nome'],
      'data': pedido['data_leitura'].strftime('%d/%m/%Y'),
      'liberacao_pagamento': liberacao_pagamento,

      'pagamento': f"{pagamento['forma_pagamento']['codigo']} - {pagamento['forma_pagamento']['nome']}",
      'cupom': cupom,
      'parcelas': pagamento['parcelamento'].get('numero_parcelas', 0),
      'código': pagamento['transacao_id'],

      'disponibilidade': disponibilidade,
      'prazo_envio': add_util_days(pedido['data_leitura'], disponibilidade).strftime('%d/%m/%Y'),
      'prazo_frete': int(envio['prazo']) - disponibilidade,
      'envio': f"{envio['forma_envio']['nome']} - {envio['forma_envio']['tipo']}",
      'estado': pedido['endereco_entrega']['estado'],

      'subtotal': to_money(pedido['valor_subtotal']),
      'desconto': to_money(pedido['valor_desconto']),
      'frete': to_money(pedido['valor_envio']),
      'total': to_money(pedido['valor_total']),
      'taxas': to_money(sum([float(value) for value in detalhe_pagamento.get('creditorFees', {}).values()])),
      'total_líquido': to_money(total_liquido),    
      'custo': to_money(custo),
      'lucro_bruto': to_money(lucro_bruto),
    }

  def send_mail(self, csv_path:str):
    if not self.email_to:
      return

    br_date_i = self.datas[0].strftime('%d/%m/%Y')
    br_date_f = self.datas[-1].strftime('%d/%m/%Y')

    subject = f"Dados do dia {br_date_i}"
    body = f'Bom dia \n\nsegue em anexo os pedidos pagos do dia {br_date_i}'
    files_to_send=[{'name': 'Pedidos Pagos', 'file': csv_path}]

    if self.datas[0] != self.datas[-1]:
      subject += f" ao dia {br_date_f}"
      body += f' ao dia {br_date_f}'

    mailer.send(email_to=self.email_to,
                subject=subject,
                body=body,
                files_to_send=files_to_send)
