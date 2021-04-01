# -*- coding: utf-8 -*-

import sys
from pprint import pprint

from lojaintegrada import LojaIntegrada
from helpers import add_util_days, to_money, to_csv, mailer


def pedido_mapper(pedido):
  cliente = pedido['cliente']
  envio = pedido['envios'][0]
  pagamento = pedido['pagamentos'][0]

  disponibilidade = max(map(lambda item: int(item['disponibilidade']), pedido['itens']))
  cupom = ''
  if pedido['cupom_desconto'] is not None:
    cupom = pedido['cupom_desconto'].get('codigo', '')

  return {
    'cliente': cliente['nome'],
    'pedido': pedido['numero'],
    'data': str(pedido['data_leitura']),

    'pagamento': f"{pagamento['forma_pagamento']['codigo']} - {pagamento['forma_pagamento']['nome']}",
    'cupom': cupom,
    'parcelas': pagamento['parcelamento'].get('numero_parcelas', 0),
    'código': pagamento['transacao_id'],
    'situação': pedido['situacao']['nome'],

    'envio': f"{envio['forma_envio']['nome']} - {envio['forma_envio']['tipo']}",
    'disponibilidade': disponibilidade,
    'prazo_envio': str(add_util_days(pedido['data_leitura'], disponibilidade)),
    'prazo_frete': int(envio['prazo']) - disponibilidade,
    'estado': pedido['endereco_entrega']['estado'],

    'subtotal': to_money(pedido['valor_subtotal']),
    'desconto': to_money(pedido['valor_desconto']),
    'frete': to_money(pedido['valor_envio']),
    'custo': to_money(sum(map(lambda item: float(item['preco_custo']), pedido['itens']))),
    'total': to_money(pedido['valor_total']),
  }


def main(LI:LojaIntegrada, data, email_to:list):
  atualizacoes = LI.lista_atualizacoes_por_data(data)
  pedidos_pagos = atualizacoes.get('pedido_pago', [])
  pedidos = []

  if not pedidos_pagos:
    sys.exit(0, f"Nenhum pedido pago para a data {data}\n")

  for atualizacao in pedidos_pagos:
    pedido = LI.get_pedido_info(atualizacao['numero'])
    pedido['data_leitura'] = data
    pedidos.append(pedido_mapper(pedido))

  csv_path = to_csv(pedidos)

  if email_to:
    br_date = data.strftime('%d/%m/%Y')
    mailer.send(email_to=email_to,
                subject=f"Dados do dia {br_date}",
                body=f'Bom dia \n\nsegue em anexo os pedidos pagos do dia {br_date}.',
                files_to_send=[{'name': 'Pedidos Pagos', 'file': csv_path}])