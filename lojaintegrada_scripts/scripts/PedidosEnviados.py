# -*- coding: utf-8 -*-

import logging
import xlsxwriter
from os import path

from envios import Envio
from plataformas import PlataformaABC
from helpers import mailer

logger = logging.getLogger(__name__)
CWD = path.dirname(path.abspath(__file__))
TMP = path.join(CWD, '..', 'tmp')

class PedidosEnviados:
  def __init__(self, plataforma:PlataformaABC, email_to:list):
    self.plataforma = plataforma
    self.email_to=email_to

  def __call__(self):
    logger.info(f'buscando pedidos enviados')
    pedidos_enviados = self.plataforma.lista_pedidos_enviados()
    logger.info('pedidos obtidos com sucesso')

    pedidos = []

    for pedido in pedidos_enviados:
      pedidos.append(self.check_pedido(pedido['numero']))

    if pedidos:
      xlsx_path = self.to_excel(pedidos)
      self.send_mail(xlsx_path)

  def check_pedido(self, numero:int):
    logger.debug(f'Executando pedido {numero}')
    
    pedido = self.plataforma.get_pedido_info(numero)
    pedido['rastreio'] = {}
    codigo_rastreio = pedido['envios'][0]['objeto']

    if codigo_rastreio:
      pedido['rastreio'] = Envio.track(codigo_rastreio)

    return self.pedido_mapper(pedido)

  def pedido_mapper(self, pedido):    
    last_event = pedido['rastreio'].get('objeto', [{}])[0].get('evento', [{}])[0]
    cep_destino = last_event.get('cepDestino', '')
    if cep_destino:
      cep_destino = f'{cep_destino[:5]}-{cep_destino[5:]}'

    return {
      'pedido': pedido['numero'],
      'cep_destino': cep_destino,
      'data_postagem': last_event.get('dataPostagem', ''),
      'objeto': pedido['envios'][0]['objeto'],
      'data': last_event.get('data', ''),
      'descricao': last_event.get('descricao', ''),
    }

  def send_mail(self, file_path:str):
    logger.info("Enviando email")
    if not self.email_to:
      logger.error("Email não enviado")
      return

    subject = f"Atualização de pedidos enviados"
    body = f'Bom dia \n\nsegue em anexo o resumo de pedidos enviados'
    files_to_send=[{'name': 'Pedidos Enviados', 'file': file_path}]

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
      self._write_excel_row(workbook, worksheet, row, row, pedido)
      row += 1

    workbook.close()
    return file_path

  def _write_excel_row(self, workbook, worksheet, first_row, last_row, row_data):
    col = -1
    body_format = workbook.add_format({
      'font_size': 9,
      'align': 'left',
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
