class InvalidTransactionCodeError(Exception):
  def __init__(self, codigo_transacao):
    super().__init__(f'Código de Transação MercadoPago Inválido: {codigo_transacao}')
