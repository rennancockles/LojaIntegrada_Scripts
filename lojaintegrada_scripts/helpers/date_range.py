from datetime import datetime, timedelta, date

def date_range(data_i, data_f=None)->list[date]:
  if data_f is None:
    data_f = data_i

  data_i = datetime.strptime(data_i, '%d/%m/%Y')
  data_f = datetime.strptime(data_f, '%d/%m/%Y')

  if data_f < data_i:
    data_i, data_f = data_f, data_i
    
  return [(data_i + timedelta(days=x)).date() for x in range((data_f-data_i).days+1)]
