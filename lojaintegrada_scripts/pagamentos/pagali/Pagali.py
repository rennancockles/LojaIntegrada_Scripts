from pagamentos.errors import InvalidTransactionCodeError
from pagamentos.PagamentoABC import PagamentoABC


class Pagali(PagamentoABC):
    TAX_PERCENT = 0.01

    def consulta_detalhe_transacao(self, pagamento):
        codigo_transacao = pagamento["transacao_id"]

        if not self._is_codigo_valido(codigo_transacao):
            raise InvalidTransactionCodeError(self, codigo_transacao)

        valor_pago = float(pagamento["valor_pago"])
        taxas = round(valor_pago * self.TAX_PERCENT, 2)
        total_liquido = round(valor_pago - taxas, 2)
        liberacao_pagamento = pagamento["data"].strftime("%d/%m/%Y")

        return {
            "total_liquido": total_liquido,
            "liberacao_pagamento": liberacao_pagamento,
            "taxas": taxas,
        }

    @staticmethod
    def _is_codigo_valido(codigo_transacao):
        return len(codigo_transacao.replace("-", "")) == 10
