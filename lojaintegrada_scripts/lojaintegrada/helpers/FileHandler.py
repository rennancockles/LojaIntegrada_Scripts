import os
import logging 
import pickle
from datetime import date, datetime

logger = logging.getLogger(__name__)

class FileHandler:
  extension = '.pkl'

  def __init__(self, base_directory:str):
    self.base_directory = base_directory
    self.check_directory()

  def check_directory(self):
    if not os.path.exists(self.base_directory):
      os.makedirs(self.base_directory)
  
  def split_filename(self, filename:str)->tuple[str, date, date, str]:
    filename, extension = filename.rsplit('.', 1)
    filename, date_f = filename.rsplit('_', 1)
    filename, date_i = filename.rsplit('_', 1)
    date_i = datetime.strptime(date_i, '%Y-%m-%d').date()
    date_f = datetime.strptime(date_f, '%Y-%m-%d').date()
    return filename, date_i, date_f, extension
  
  def export(self, filename:str, dados:dict):
    if not filename.endswith(self.extension):
      filename += self.extension
    
    with open(os.path.join(self.base_directory, filename), "wb") as file_:
      logger.debug(f'exportando dados para {filename}')
      pickle.dump(dados, file_)
      
  def _find_import_file(self, filename:str):
    filename, date_i, date_f, _ = self.split_filename(filename)
    file_list = [f for f in os.listdir(self.base_directory) 
                 if os.path.isfile(os.path.join(self.base_directory, f)) 
                 and f.startswith(filename)]

    logger.debug(f'possiveis arquivos encontrados: {file_list}')

    for file_ in file_list:
      _, file_date_i, file_date_f, _ = self.split_filename(file_)

      if file_date_i <= date_i and file_date_f >= date_f:
        logger.debug(f'arquivo encontrado: {file_}')
        return os.path.join(self.base_directory, file_)
  
  def import(self, filename:str):
    if not filename.endswith(self.extension):
      filename += self.extension

    file_path = self._find_import_file(filename)

    if os.path.exists(file_path):
      with open(file_path, "rb") as file_:
        logger.debug(f'importando dados de {filename}')
        return pickle.load(file_)
    return []
