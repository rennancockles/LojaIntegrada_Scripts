def to_money(valor):
  if valor is None or valor == '':
    return ''
  if type(valor) == str:
    valor = float(valor)
  valor_str = 'R$ {0:,.2f}'.format(valor).replace(',', '.')
  return valor_str[0:-4] + valor_str[-4:].replace('.', ',')
