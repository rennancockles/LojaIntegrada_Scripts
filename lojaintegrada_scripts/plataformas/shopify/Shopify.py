from plataformas.errors import ResponseError
from plataformas import PlataformaABC

import requests


class Shopify(PlataformaABC):
  _base_url = 'https://{api_key}:{password}@{store}.myshopify.com/admin/api/2021-04'

  def __init__(self, api_key:str, password:str, store:str):
    self.store = store.title()
    self._base_url = self._base_url.format(api_key=api_key, password=password, store=store)
    self.base_params = {
      'limit': 250,
    }

  def _execute_get(self, resource, params={}):
    _params = self.base_params.copy()
    _params.update(params)

    response = requests.get(self._base_url + resource,
                            params=_params,
                            headers={'content-type': "application/json"},
                            timeout=50)

    if response.ok:
      return response.json()
    else:
      raise ResponseError(response)

  def get_pedido_info(self, id):
    return self._execute_get(f'/orders/{id}.json')
