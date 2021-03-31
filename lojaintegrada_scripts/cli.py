# -*- coding: utf-8 -*-

import argparse
import os
from datetime import datetime
from importlib import import_module
from dotenv import load_dotenv

from lojaintegrada import LojaIntegrada

load_dotenv()

api_key = os.getenv("API_KEY")
app_key = os.getenv("APP_KEY")

def main():
  parser = argparse.ArgumentParser(prog='lojaintegrada_scripts', description='Scripts para manipular dados da Loja Integrada.')
  parser.add_argument('--data', '-d', help='Data no formado %d/%m/%Y')
  parser.add_argument('--script', '-s', help='Script para ser executado', required=True)
  parser.add_argument("--mail_to", '-m', nargs="+", help="Lista de destinatários para enviar email")

  args = parser.parse_args()

  if args.data:
    try:
      data = datetime.strptime(args.data, '%d/%m/%Y').date()
    except:
      parser.exit(1, "Data no formato inválido: a data deve estar no formato %d/%m/%Y\n")
  else:
    data = datetime.today().date()

  try:
    script = import_module(f'scripts.{args.script}')
  except:
    parser.exit(1, f"Script não encontrado: {args.script}\n")

  LI = LojaIntegrada(api_key=api_key, app_key=app_key)
  script.main(LI, data, email_to=args.mail_to)
