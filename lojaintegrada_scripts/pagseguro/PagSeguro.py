from .errors import InvalidTransactionCodeError, InvalidCredentialError

import requests
import xmltodict


class PagSeguro:
  _base_url = 'https://ws.pagseguro.uol.com.br'

  def __init__(self, email:str, token:str):
    self.base_params = {
      'email': email,
      'token': token
    }
    self._testa_sessao()

  def _execute_post(self, resource, params={}):
    _params = self.base_params.copy()
    _params.update(params)

    response = requests.post(self._base_url + resource,
                            params=_params,
                            timeout=50)

    if response.ok:
      return xmltodict.parse(response.content)
    else:
      return None

  def _execute_get(self, resource, params={}):
    _params = self.base_params.copy()
    _params.update(params)

    response = requests.get(self._base_url + resource,
                            params=_params,
                            timeout=50)

    if response.ok:
      return xmltodict.parse(response.content)
    else:
      return None

  def _testa_sessao(self):
    response = self._execute_post('/v2/sessions')
    if not response or type(response['session']['id'] != str):
      raise InvalidCredentialError()

  def consulta_detalhe_transacao(self, codigo_transacao):
    if not self._is_codigo_valido(codigo_transacao):
      raise InvalidTransactionCodeError(codigo_transacao)
    return self._execute_get(f'/v3/transactions/{codigo_transacao}')
  
  @staticmethod
  def _is_codigo_valido(codigo_transacao):
    return len(codigo_transacao.replace('-', '')) == 32
