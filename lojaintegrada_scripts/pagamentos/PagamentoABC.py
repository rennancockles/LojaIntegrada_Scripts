# -*- coding: UTF-8 -*-

from abc import ABC, abstractmethod


class PagamentoABC(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def _is_codigo_valido(codigo_transacao):
        pass

    @abstractmethod
    def consulta_detalhe_transacao(self, codigo_transacao):
        pass
