def to_money(valor, currency:str=""):
  if valor is None or valor == '':
    return ''
  if type(valor) == str:
    valor = float(valor)
  valor_str = '{0:,.2f}'.format(valor).replace(',', '.')
  if currency:
    valor_str = f'{currency.strip()} {valor_str}'
  return valor_str[0:-4] + valor_str[-4:].replace('.', ',')
