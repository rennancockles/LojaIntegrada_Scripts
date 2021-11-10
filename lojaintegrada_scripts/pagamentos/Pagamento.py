# -*- coding: UTF-8 -*-

import os

from .mercadopago import MercadoPago
from .pagali import Pagali
from .pagseguro import PagSeguro


class Pagamento:
    pagseguro = PagSeguro(
        email=os.getenv("PAGSEGURO_EMAIL"), token=os.getenv("PAGSEGURO_TOKEN")
    )
    mercadopago = MercadoPago(token=os.getenv("MERCADOPAGO_TOKEN"))
    pagali = Pagali()

    @classmethod
    def _get_instance(cls, forma_pagamento):
        return {
            "pagsegurov2": cls.pagseguro,
            "psboleto": cls.pagseguro,
            "mercadopagov1": cls.mercadopago,
            "mpboleto": cls.mercadopago,
            "pagali-pix": cls.pagali,
        }.get(forma_pagamento, None)

    @classmethod
    def consulta_detalhe_transacao(cls, pagamento, data):
        pagamento["data"] = data
        forma_pagamento = pagamento["forma_pagamento"]["codigo"]
        transacao_id = pagamento["transacao_id"]

        if (
            not forma_pagamento
            or not transacao_id
            or not (PG_CLASS := Pagamento._get_instance(forma_pagamento))
        ):
            return {}

        response = PG_CLASS.consulta_detalhe_transacao(pagamento) or {}
        return response
