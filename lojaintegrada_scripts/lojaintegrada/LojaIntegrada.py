from lojaintegrada.LojaIntegradaAPI import LojaIntegradaAPI
from lojaintegrada.errors import APIError
from lojaintegrada.helpers import to_date

from datetime import date


class LojaIntegrada(LojaIntegradaAPI):
  def __init__(self, api_key:str, app_key:str):
    super().__init__(api_key, app_key)

  def _filtra_response_por_data(self, response, data):
    update_ids = set()
    result = {
      'data': []
    }

    for r in response:
      if to_date(r["data"]) == data and r['id'] not in update_ids:
        if not result.get(r['situacao']['codigo'], None):
          result[r['situacao']['codigo']] = []

        update_ids.add(r['id'])
        result['data'].append(r)
        result[r['situacao']['codigo']].append(r)

    return result

  def lista_atualizacoes_por_data(self, data:date, limit:int=20):
    dados = []
    response = self.lista_historico_situacao(limit=1)
    total = response['meta']['total_count']
    offset = total

    while True:
      offset -= limit
      response = self.lista_historico_situacao(offset=offset, limit=limit)

      if not response.get('meta', False):
        raise APIError(response)

      meta = response['meta']
      dados += response['objects']

      first_date = response['objects'][0]['data']
      last_date = response['objects'][-1]['data']

      if to_date(first_date) < data or to_date(last_date) < data or not meta.get('previous', False):
        break

    return self._filtra_response_por_data(dados, data)