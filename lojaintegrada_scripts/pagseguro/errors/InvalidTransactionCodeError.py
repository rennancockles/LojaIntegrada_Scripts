class InvalidTransactionCodeError(Exception):
  def __init__(self, codigo_transacao):
    super().__init__(f'Código de Transação PagSeguro Inválido: {codigo_transacao}')
