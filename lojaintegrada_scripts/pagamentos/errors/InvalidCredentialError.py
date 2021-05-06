class InvalidCredentialError(Exception):
  def __init__(self, parent):
    super().__init__(f'Credencial {parent.__class__.__name__} Inválida')
