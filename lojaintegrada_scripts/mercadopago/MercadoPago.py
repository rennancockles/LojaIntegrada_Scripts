from .errors import InvalidTransactionCodeError, InvalidCredentialError

import requests


# docs: https://developers.mercadolivre.com.br/pt_br/gerenciamento-de-pagamentos
class MercadoPago:
  _base_url = 'https://api.mercadopago.com'

  def __init__(self, token:str):
    self.access_token = token
    self.base_params = {}
    self.headers = { 'Authorization': 'Bearer ' + token }

  def _execute_get(self, resource, params={}):
    _params = self.base_params.copy()
    _params.update(params)

    response = requests.get(self._base_url + resource,
                            params=_params,
                            headers=self.headers,
                            timeout=50)

    if response.ok:
      return self.adapt_response(response.json())
    else:
      return None

  def consulta_detalhe_transacao(self, codigo_transacao):
    if not self._is_codigo_valido(codigo_transacao):
      raise InvalidTransactionCodeError(codigo_transacao)
    return self._execute_get(f'/v1/payments/{codigo_transacao}')
  
  def adapt_response(self, response):
    fee_details = filter(lambda fee: fee.get('fee_payer', '') == 'collector', response.get('fee_details', []))
    creditorFees = {fee['type']:fee['amount'] for fee in fee_details}
    return {
      'transaction': {
        'netAmount': response.get('transaction_details', {}).get('net_received_amount', ''),
        'escrowEndDate': response.get('money_release_date', ''),
        'creditorFees': creditorFees
      }
    }
  
  @staticmethod
  def _is_codigo_valido(codigo_transacao):
    return len(codigo_transacao.replace('-', '')) == 11
