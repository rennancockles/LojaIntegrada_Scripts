# -*- coding: UTF-8 -*-

import re
from .correios import Correios

class Envio:  
  @staticmethod
  def is_correios(codigo:str) -> bool:
    return re.match('^[a-zA-Z]{2}[0-9]{9}[a-zA-Z]{2}$', codigo)

  @staticmethod
  def track(codigo):
    if not codigo:
      return {}
  
    if Envio.is_correios(codigo):
      return Correios.track(codigo)

    return {}

