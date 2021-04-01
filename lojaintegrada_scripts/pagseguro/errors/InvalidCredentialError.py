class InvalidCredentialError(Exception):
  def __init__(self):
    super().__init__(f'Credencial PagSeguro Inválida')
