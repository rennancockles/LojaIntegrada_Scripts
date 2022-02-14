# -*- coding: UTF-8 -*-

from abc import ABC, abstractmethod


class EnvioABC(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def track(self, codigo):
        pass
