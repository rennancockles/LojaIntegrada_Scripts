from pagamentos.errors import InvalidTransactionCodeError, InvalidCredentialError
from pagamentos import PagamentoABC

import requests
import xmltodict


class PagSeguro(PagamentoABC):
  _base_url = 'https://ws.pagseguro.uol.com.br'

  STATUS = (
    (1, 'Aguardando pagamento'),
    (2, 'Em análise'),
    (3, 'Aprovado'),
    (4, 'Disponível'),
    (5, 'Em disputa'),
    (6, 'Devolvido'),
    (7, 'Cancelado'),
    (8, 'Debitado'),
    (9, 'Retenção Temporária')
  )

  TIPO_PAGAMENTO = (
    (1, 'Crédito'),
    (2, 'Boleto'),
    (3, 'Débito online'),
    (4, 'Saldo PagSeguro'),
    (5, 'Oi paggo'),
    (6, ''),
    (7, 'Depósito em conta')
  )

  COD_PAGAMENTO = (
    (101, 'Visa'), (102, 'MasterCard'), (103, 'American Express'), (104, 'Diners'), (105, 'Hipercard'),
    (106, 'Aura'), (107, 'Elo'), (108, 'PLENOCard'), (109, 'PersonalCard'), (110, 'JCB'),
    (111, 'Discover'), (112, 'BrasilCard'), (113, 'FORTBRASIL'), (114, 'CARDBAN'), (115, 'VALECARD'),
    (116, 'Cabal'), (117, 'Mais!'), (118, 'Avista'), (119, 'GRANDCARD'), (120, 'Sorocred'),
    (201, 'Bradesco'), (202, 'Santander'), (203, 'Nubank'),
    (301, 'Bradesco'), (302, 'Itaú'), (303, 'Unibanco'), (304, 'Banco do Brasil'), (305, 'Banco Real'),
    (306, 'Banrisul'), (307, 'HSBC'),
    (401, 'Saldo PagSeguro'),
    (501, 'Oi paggo'),
    (701, 'Banco do Brasil'), (702, 'HSBC'), (703, 'Itaú'), (704, 'Caixa')
  )

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
      return self.adapt_response(xmltodict.parse(response.content))
    else:
      return None

  def _testa_sessao(self):
    response = self._execute_post('/v2/sessions')
    if not response or type(response['session']['id']) != str:
      raise InvalidCredentialError(self)

  def consulta_detalhe_transacao(self, codigo_transacao):
    if not self._is_codigo_valido(codigo_transacao):
      raise InvalidTransactionCodeError(self, codigo_transacao)
    return self._execute_get(f'/v3/transactions/{codigo_transacao}')
  
  def adapt_response(self, response):
    return response
  
  @staticmethod
  def _is_codigo_valido(codigo_transacao):
    return len(codigo_transacao.replace('-', '')) == 32
