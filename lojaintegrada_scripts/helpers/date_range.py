from datetime import datetime, timedelta

def date_range(data_i, data_f=None):
  if data_f is None:
    data_f = data_i
  data_i = datetime.strptime(data_i, '%d/%m/%Y').date()
  data_f = datetime.strptime(data_f, '%d/%m/%Y').date()
  return [data_i + timedelta(days=x) for x in range((data_f-data_i).days+1)]
