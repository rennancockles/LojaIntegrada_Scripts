class InvalidTransactionCodeError(Exception):
    def __init__(self, parent, codigo_transacao):
        super().__init__(
            f"Código de Transação {parent.__class__.__name__} Inválido: "
            f"{codigo_transacao}"
        )
