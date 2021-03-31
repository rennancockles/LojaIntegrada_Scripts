from datetime import datetime

def to_date(str_date):
  try:
    return datetime.strptime(str_date, "%Y-%m-%dT%H:%M:%S.%f").date()
  except:
    return None
