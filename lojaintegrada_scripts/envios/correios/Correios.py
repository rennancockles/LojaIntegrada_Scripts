# -*- coding: utf-8 -*-

import requests

from envios import EnvioABC


# Manual PDF: https://www.correios.com.br/a-a-z/pdf/rastreamento-de-objetos/manual_rastreamentoobjetosws.pdf
class Objeto(object):
  def __init__(self, *args, **kwargs):
    self.cepDestino = ""
    self.dataPostagem = ""
    self.eventos = list()
    self.numero = kwargs.get('numero', '')
    self.categoria = kwargs.get('categoria', '')
    self.sigla = kwargs.get('sigla', '')
    self.nome = kwargs.get('nome', '')
    self.json = ""

    if 'evento' in kwargs and len(kwargs.get('evento', list())) > 0:
      evento = kwargs.get('evento')[0]
      self.cepDestino = evento.get('cepDestino', '')
      self.dataPostagem = evento.get('dataPostagem', '')

      for evento in kwargs.get('evento', list()):
        self.eventos.append(Evento(**evento))

      # if cep != "":
      #     self.cepDestino = cep[:-3] + '-' + cep[-3:]
      # if data != "":
      #     self.dataPostagem = datetime.strptime(data, "%d/%m/%Y")


class Evento(object):
  def __init__(self, *args, **kwargs):
    self.tipo = kwargs.get('tipo', '')
    self.data = kwargs.get('data', '')
    self.hora = kwargs.get('hora', '')
    self.criacao = kwargs.get('criacao', '')
    self.prazoGuarda = kwargs.get('prazoGuarda', '')
    self.diasUteis = kwargs.get('diasUteis', '')
    self.descricao = kwargs.get('descricao', '')
    self.detalhe = kwargs.get('detalhe', '')
    self.status = kwargs.get('status', '')

    if 'unidade' in kwargs:
      self.unidade = Unidade(**kwargs.get('unidade', dict()))

    if 'destino' in kwargs and len(kwargs.get('destino', list())) > 0:
      self.destino = Destino(**kwargs.get('destino')[0])

    if 'detalheOEC' in kwargs:
      self.detalheOEC = OEC(**kwargs.get('detalheOEC', dict()))


class Unidade(object):
  def __init__(self, *args, **kwargs):
    self.tipounidade = kwargs.get('tipounidade', '')
    self.local = kwargs.get('local', '')
    self.sto = kwargs.get('sto', '')
    self.codigo = kwargs.get('codigo', '')
    self.uf = kwargs.get('uf', '')
    self.cidade = kwargs.get('cidade', '')

    if 'endereco' in kwargs:
      self.endereco = Endereco(**kwargs.get('endereco', dict()))


class Endereco(object):
  def __init__(self, *args, **kwargs):
    self.numero = kwargs.get('numero', '')
    self.cep = kwargs.get('cep', '')
    self.localidade = kwargs.get('localidade', '')
    self.bairro = kwargs.get('bairro', '')
    self.codigo = kwargs.get('codigo', '')
    self.logradouro = kwargs.get('logradouro', '')
    self.uf = kwargs.get('uf', '')
    self.latitude = kwargs.get('latitude', '')
    self.longitude = kwargs.get('longitude', '')


class Destino(object):
  def __init__(self, *args, **kwargs):
    self.bairro = kwargs.get('bairro', '')
    self.local = kwargs.get('local', '')
    self.cidade = kwargs.get('cidade', '')
    self.uf = kwargs.get('uf', '')
    self.codigo = kwargs.get('codigo', '')

    if 'endereco' in kwargs:
      self.endereco = Endereco(**kwargs.get('endereco', dict()))


class OEC(object):
  def __init__(self, *args, **kwargs):
    self.lista = kwargs.get('lista', '')
    self.longitude = kwargs.get('longitude', '')
    self.latitude = kwargs.get('latitude', '')
    self.carteiro = kwargs.get('carteiro', '')
    self.distrito = kwargs.get('distrito', '')
    self.unidade = kwargs.get('unidade', '')

    if 'endereco' in kwargs:
      self.endereco = Endereco(**kwargs.get('endereco', dict()))


class Correios(EnvioABC):
  @staticmethod
  def track(codigo):
    body = f'''
    <rastroObjeto>
      <usuario>MobileXect</usuario>
      <senha>DRW0#9F$@0</senha>
      <tipo>L</tipo>
      <resultado>T</resultado>
      <objetos>{codigo}</objetos>
      <lingua>101</lingua>
      <token>QTXFMvu_Z-6XYezP3VbDsKBgSeljSqIysM9x</token>
    </rastroObjeto>
    '''

    r = requests.post('http://webservice.correios.com.br/service/rest/rastro/rastroMobile', data=body, headers={'Content-Type': 'application/xml'})

    if r.status_code == 200:
      result = r.json().get('objeto', list())
      if result:
        objeto = Objeto(**result[0])
        objeto.json = r.json()
        return objeto.json

    return None


# def geraCodValido(cod, withCep=False):
#     cod = cod.strip()

#     if len(cod) < 12 or 13 < len(cod):
#         return ""

#     prefixo = cod[0:2]
#     numero = cod[2:10]
#     sufixo = cod[-2:]
#     multiplicadores = [8, 6, 4, 2, 3, 5, 9, 7]

#     if len(numero) < 8 and len(cod) == 12:
#         diferenca = 8 - len(numero)
#         zeros = "0" * diferenca
#         numero = zeros + numero

#     soma = sum(int(numero[i]) * multiplicadores[i] for i in range(8))
#     resto = soma % 11

#     if resto == 0:
#         dv = "5"
#     elif resto == 1:
#         dv = "0"
#     else:
#         dv = str(11 - int(resto))

#     codfinal = prefixo + numero + dv + sufixo

#     if withCep:
#         r = rastreio(codfinal)
#         return codfinal, str(r.cepDestino)

#     return codfinal


# def findCod(cod, cep, numDigits=1):
#     cep = cep.replace('-', '')

#     if numDigits == 1:
#         for i in range(10):
#             result = geraCodValido(cod[:9]+str(i)+cod[10:], True)
#             if result[1] == cep:
#                 return result
#         return findCod(cod, cep, 2)

#     elif numDigits == 2:
#         for i in range(10):
#             for j in range(10):
#                 result = geraCodValido(cod[:8] + str(i) + str(j) + cod[10:], True)
#                 if result[1] == cep:
#                     return result

#     return None, None


# if __name__ == '__main__':
#     # obj1 = 'DY195036938BR'
#     # r1 = rastreio(obj1)
#     #
#     # obj2 = 'DY195036938BT'
#     # r2 = rastreio(obj2)
#     #
#     # obj3 = 'PM403880463BR'
#     # r3 = rastreio(obj3)

#     # DANIELE CRISTINA PM124631969BR - CEP: 36401-001 => PM124631959BR
#     # LANE FACCO MOREIRA PM124631961BR - CEP: 99600-000 => PM124631931BR
#     codEncontrado = findCod('PM124631969BR', '36401-331')
#     codEncontrado2 = findCod('PM124631961BR', '99600-000')
