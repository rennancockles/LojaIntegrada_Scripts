# -*- coding: utf-8 -*-

import logging
from datetime import date
from os import path

from helpers import to_money
from plataformas import PlataformaABC

logger = logging.getLogger(__name__)
CWD = path.dirname(path.abspath(__file__))
TMP = path.join(CWD, "..", "tmp")


class TotalPago:
    def __init__(self, plataforma: PlataformaABC, datas: list[date]):
        self.plataforma = plataforma
        self.datas = datas

    def run(self):
        logger.info(f"buscando atualizacoes entre {self.datas[0]} e {self.datas[-1]}")
        atualizacoes = self.plataforma.lista_atualizacoes_por_datas(self.datas)
        logger.info("atualizacoes obtidas com sucesso")

        total = 0

        for data in self.datas:
            logger.info(f"executando para a data {data}")
            atualizacoes_pedidos_pagos = atualizacoes.get(str(data), {}).get(
                "pedido_pago", []
            )

            total += self.get_total(atualizacoes_pedidos_pagos, data)

        logger.info(f"Total {to_money(total)}")

    def get_total(self, atualizacoes_pedidos_pagos, data: date):
        logger.info(f"{len(atualizacoes_pedidos_pagos)} pedidos pagos")
        total = 0

        for atualizacao in sorted(
            atualizacoes_pedidos_pagos, key=lambda at: at["numero"]
        ):
            pedido = self.plataforma.get_pedido_info(atualizacao["numero"])
            total += float(pedido["valor_total"])
            logger.debug(
                f"Pedido {pedido['numero']} => {to_money(pedido['valor_total'])}"
            )

        return total
