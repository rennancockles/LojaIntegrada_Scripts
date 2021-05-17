# -*- coding: utf-8 -*-

from .LojaIntegradaAPI import LojaIntegradaAPI
from plataformas.errors import APIError
from plataformas.helpers import to_date, FileHandler

import logging
import os
from datetime import date

logger = logging.getLogger(__name__)
CWD = os.path.dirname(os.path.abspath(__file__))
DATA_DIRECTORY = os.path.join(CWD, 'dados')
MIN_DAYS_TO_EXPORT = 7


class LojaIntegrada(LojaIntegradaAPI):
  def __init__(self, api_key:str, app_key:str, store:str=''):
    super().__init__(api_key, app_key)
    self.store = store.title()
    self.fileHandler = FileHandler(DATA_DIRECTORY)

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

  def _filtra_response_por_datas(self, response, datas:list[date]):
    def verify_result(r):
      response_date = to_date(r["data"])
      if not result.get(str(response_date), None):
        result[str(response_date)] = {}
      if not result[str(response_date)].get(r['situacao']['codigo'], None):
        result[str(response_date)][r['situacao']['codigo']] = []
      return result[str(response_date)][r['situacao']['codigo']]

    data_i = datas[0]
    data_f = datas[-1]
    update_ids = set()
    result = {
    }

    for r in response:
      response_date = to_date(r["data"])
      if r['id'] in update_ids:
        logger.debug(f'histórico já executado: {r["id"]}')
        continue

      if response_date >= data_i and response_date <= data_f:
        _result = verify_result(r)
        _result.append(r)

        update_ids.add(r['id'])

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

  def lista_atualizacoes_por_datas(self, datas:list[date], limit:int=20):
    if len(datas) == 0:
      return None

    data_i = datas[0]
    data_f = datas[-1]
    filename = f'atualizacoes_por_datas_{data_i}_{data_f}'
    dados = self.fileHandler.import_file(filename)
    if dados:
      logger.debug(f'retornando dados importados')
      return dados

    response = self.lista_historico_situacao(limit=1)
    total = response['meta']['total_count']
    logger.debug(f'total historico situacoes: {total}')
    offset = total

    while True:
      offset -= limit
      response = self.lista_historico_situacao(offset=offset, limit=limit)

      if not response.get('meta', False):
        raise APIError(response)

      meta = response['meta']

      first_date = to_date(response['objects'][0]['data'])

      if first_date <= data_f:
        dados += response['objects']

      if first_date < data_i or not meta.get('previous', False):
        break

    logger.debug(f'offset final: {offset}')
    logger.debug(f'{len(dados)} dados obtidos')
    dados_filtrados = self._filtra_response_por_datas(dados, datas)

    if (data_f - data_i).days >= MIN_DAYS_TO_EXPORT:
      self.fileHandler.export_file(filename, dados_filtrados)

    return dados_filtrados

  def lista_pedidos_enviados(self, limit:int=20):
    offset = 0
    dados = []

    while True:
      response = self.lista_pedidos(situacao_id=11, offset=offset, limit=limit)

      if not response.get('meta', False):
        raise APIError(response)

      meta = response['meta']
      dados += response['objects']

      if not meta.get('next', False):
        break
      
      offset += limit

    return dados
