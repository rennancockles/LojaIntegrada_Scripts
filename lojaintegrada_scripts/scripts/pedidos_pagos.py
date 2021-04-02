# -*- coding: utf-8 -*-

import logging
import os
from datetime import datetime, date

from lojaintegrada import LojaIntegrada
from pagseguro import PagSeguro
from helpers import add_util_days, to_money, to_csv, mailer

logger = logging.getLogger(__name__)

def pedido_mapper(pedido):
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

def main(LI:LojaIntegrada, datas:list[date], email_to:list):
  pagseguro = PagSeguro(email=os.getenv("PAGSEGURO_EMAIL"), token=os.getenv("PAGSEGURO_TOKEN"))

  logger.info(f'buscando atualizacoes entre {datas[0]} e {datas[-1]}')
  atualizacoes = LI.lista_atualizacoes_por_datas(datas)
  logger.info('atualizacoes obtidas com sucesso')

  for data in datas:
    logger.info(f'executando para a data {data}')
    atualizacoes_pedidos_pagos = atualizacoes.get(str(data), {}).get('pedido_pago', [])

    logger.info(f'{len(atualizacoes_pedidos_pagos)} pedidos pagos')
    pedidos = []

    for atualizacao in atualizacoes_pedidos_pagos:
      pedido = LI.get_pedido_info(atualizacao['numero'])
      pedido['data_leitura'] = data
      pedido['detalhe_pagamento'] = {}
      
      if pedido['pagamentos'][0]['transacao_id']:
        pedido['detalhe_pagamento'] = pagseguro.consulta_detalhe_transacao(pedido['pagamentos'][0]['transacao_id'])

      pedidos.append(pedido_mapper(pedido))

    if not pedidos:
      continue
    
    csv_path = to_csv(pedidos)

    if email_to:
      br_date = data.strftime('%d/%m/%Y')
      mailer.send(email_to=email_to,
                  subject=f"Dados do dia {br_date}",
                  body=f'Bom dia \n\nsegue em anexo os pedidos pagos do dia {br_date}.',
                  files_to_send=[{'name': 'Pedidos Pagos', 'file': csv_path}])
