import requests

from plataformas.decorators import retry
from plataformas.errors import ResponseError
from plataformas.PlataformaABC import PlataformaABC


class LojaIntegradaAPI(PlataformaABC):
    _base_url = "https://api.awsli.com.br/v1"

    def __init__(self, api_key: str, app_key: str):
        self.base_params = {
            "format": "json",
            "limit": 20,
            "offset": 0,
            "chave_api": api_key,
            "chave_aplicacao": app_key,
        }

    @retry
    def _execute_get(self, resource, params={}):
        _params = self.base_params.copy()
        _params.update(params)

        response = requests.get(
            self._base_url + resource,
            params=_params,
            headers={"content-type": "application/json"},
            timeout=50,
        )

        if response.ok:
            return response.json()
        else:
            raise ResponseError(response)

    @retry
    def _execute_put(self, resource, data=""):
        _params = self.base_params.copy()

        response = requests.put(
            self._base_url + resource,
            data=data,
            params=_params,
            headers={"content-type": "application/json"},
            timeout=50,
        )

        if response.ok:
            return response.json()
        else:
            raise ResponseError(response)

    def lista_pedidos(
        self,
        since_numero=None,
        since_atualizado=None,
        cliente_id=None,
        pagamento_id=None,
        situacao_id=None,
        since_criado=None,
        until_criado=None,
        limit=20,
        offset=0,
    ):
        params = {
            k: v
            for k, v in vars().items()
            if not k.startswith("_") and k != "self" and v
        }
        return self._execute_get("/pedido/search/", params)

    def lista_historico_situacao(self, limit=20, offset=0):
        params = {
            k: v
            for k, v in vars().items()
            if not k.startswith("_") and k != "self" and v
        }
        return self._execute_get("/situacao_historico", params)

    def get_pedido_info(self, id):
        return self._execute_get(f"/pedido/{id}")

    def lista_formas_pagamentos(self):
        return self._execute_get("/pagamento")

    def get_forma_pagamento_info(self, id):
        return self._execute_get(f"/pagamento/{id}")

    def update_situacao_pedido(self, id, codigo_situacao):
        self._execute_put(
            f"/situacao/pedido/{id}", f'{{"codigo": "{codigo_situacao}"}}'
        )
        return self.get_situacao_pedido(id)

    def get_situacao_pedido(self, id):
        return self._execute_get(f"/situacao/pedido/{id}")
