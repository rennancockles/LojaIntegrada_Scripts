# -*- coding: utf-8 -*-

import logging
from datetime import datetime
from os import path
from pathlib import Path

from plataformas import PlataformaABC
from helpers import to_money, month_names

logger = logging.getLogger(__name__)
CWD = path.dirname(path.abspath(__file__))


class Declaracao:
  def __init__(self, plataforma:PlataformaABC, pedido_id:int):
    if not pedido_id:
      raise Exception('Id do Pedido não informado!')

    self.plataforma = plataforma
    self.pedido_id = pedido_id

  def __call__(self):
    logger.info(f'buscando dados do pedido {self.pedido_id}')
    pedido = self.plataforma.get_pedido_info(self.pedido_id)
    dados_declaracao = self.pedido_mapper(pedido.get('order', {}))
    logger.info('dados obtidos com sucesso')

    self.gera_declaracao(dados_declaracao)

  def pedido_mapper(self, pedido):
    today = datetime.today()
    shipping_address = pedido['shipping_address']
    shipping_line = pedido['shipping_lines'][0] if pedido['shipping_lines'] else {}
    line_items = pedido['line_items']

    itm_lines = [{
      'itm_count': i+1,
      'itm_name': line['name'],
      'itm_qty': int(line['quantity']),
      'itm_price': int(line['quantity']) * float(line['price'])
    } for i, line in enumerate(line_items)]

    return {
      'store': self.plataforma.store,
      'order_number': pedido['order_number'],

      'shp_name': shipping_address['name'],
      'shp_address1': shipping_address['address1'],
      'shp_address2': shipping_address['address2'],
      'shp_city': shipping_address['city'],
      'shp_province': shipping_address['province_code'],
      'shp_zip': shipping_address['zip'],
      'shp_doc': '',
      'shp_method': shipping_line.get('title', '_'*10),

      'itm_lines': itm_lines,

      'ord_qty': sum([line['itm_qty'] for line in itm_lines]),
      'ord_value': to_money(sum([line['itm_price'] for line in itm_lines]), currency="R$"),

      'day': today.strftime('%d') ,
      'month': month_names[int(today.strftime('%m'))],
      'year': today.strftime('%Y') ,
    }

  def gera_declaracao(self, dados):
    with open(path.join(CWD, '../templates/declaracao.html'), 'r', encoding='utf-8') as f:
      html = f.read()
      
    with open(path.join(CWD, '../templates/declaracao_item.html'), 'r', encoding='utf-8') as f:
      html_item = f.read()
      
    with open(path.join(CWD, '../templates/print.css'), 'r', encoding='utf-8') as f:
      css = f.read()

    itm_lines = [html_item.replace('@itm_count', str(line['itm_count'])) \
                          .replace('@itm_name', str(line['itm_name'])) \
                          .replace('@itm_qty', str(line['itm_qty'])) \
                          .replace('@itm_price', to_money(line['itm_price'], currency="R$"))
                for line in dados['itm_lines']]

    declaracao = html.replace('@css', f'<style>{css}</style>') \
                      .replace('@store_upper', dados['store'].upper()) \
                      .replace('@store', dados['store']) \
                      .replace('@shp_name_upper', dados['shp_name'].upper()) \
                      .replace('@shp_name', dados['shp_name']) \
                      .replace('@shp_address1', dados['shp_address1']) \
                      .replace('@shp_address2', dados['shp_address2'] or '') \
                      .replace('@shp_city', dados['shp_city']) \
                      .replace('@shp_province', dados['shp_province']) \
                      .replace('@shp_zip', dados['shp_zip']) \
                      .replace('@shp_doc', dados['shp_doc']) \
                      .replace('@shp_method', dados['shp_method']) \
                      .replace('@itm_line', '\n'.join(itm_lines)) \
                      .replace('@ord_qty', str(dados['ord_qty'])) \
                      .replace('@ord_value', dados['ord_value']) \
                      .replace('@day', dados['day']) \
                      .replace('@month', dados['month']) \
                      .replace('@year', dados['year'])

    with open(path.join(Path.home(), 'Desktop',f'{dados["order_number"]}_declaracao.html'), 'w', encoding='utf-8') as f:
      f.write(declaracao)