# -*- coding: UTF-8 -*-

from abc import ABC, abstractmethod


class PlataformaABC(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def _execute_get(self, resource, params={}):
        pass

    @abstractmethod
    def get_pedido_info(self, id):
        pass
