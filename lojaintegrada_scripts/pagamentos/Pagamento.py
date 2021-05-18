# -*- coding: UTF-8 -*-

import os
from .pagseguro import PagSeguro
from .mercadopago import MercadoPago

class Pagamento:
  pagseguro = PagSeguro(email=os.getenv("PAGSEGURO_EMAIL"), token=os.getenv("PAGSEGURO_TOKEN"))
  mercadopago = MercadoPago(token=os.getenv("MERCADOPAGO_TOKEN"))
  
  @staticmethod
  def is_pagseguro(codigo:str) -> bool:
    return codigo in ['pagsegurov2', 'psboleto']

  @staticmethod
  def is_mercadopago(codigo:str) -> bool:
    return codigo in ['mercadopagov1', 'mpboleto']

  @classmethod
  def _get_instance(cls, forma_pagamento):
    if Pagamento.is_pagseguro(forma_pagamento):
      return cls.pagseguro
    elif Pagamento.is_mercadopago(forma_pagamento):
      return cls.mercadopago
    else:
      return None

  @classmethod
  def consulta_detalhe_transacao(cls, forma_pagamento, transacao_id):
    if not forma_pagamento or not transacao_id:
      return {}

    PG_CLASS = Pagamento._get_instance(forma_pagamento)
    if PG_CLASS is None:
      return {}
      
    return PG_CLASS.consulta_detalhe_transacao(transacao_id) or {}
