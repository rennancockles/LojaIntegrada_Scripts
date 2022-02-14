# -*- coding: UTF-8 -*-

import os

from .lojaintegrada import LojaIntegrada
from .shopify import Shopify


class Plataforma:
    shopify = Shopify(
        api_key=os.getenv("SHOPIFY_API_KEY"),
        password=os.getenv("SHOPIFY_PASSWORD"),
        store=os.getenv("SHOPIFY_STORE"),
    )
    lojaintegrada = LojaIntegrada(
        api_key=os.getenv("LI_API_KEY"),
        app_key=os.getenv("LI_APP_KEY"),
        store=os.getenv("LI_STORE"),
    )
    plataformas = {
        "shopify": shopify,
        "lojaintegrada": lojaintegrada,
    }

    def get_plataforma(nome: str):
        return Plataforma.plataformas.get(nome.lower(), None)
