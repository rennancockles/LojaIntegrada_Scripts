# -*- coding: utf-8 -*-

import argparse
import os
import logging
from datetime import datetime
from importlib import import_module
from dotenv import load_dotenv

from lojaintegrada import LojaIntegrada
from helpers import date_range

load_dotenv()

api_key = os.getenv("API_KEY")
app_key = os.getenv("APP_KEY")


def parse_args():
  parser = argparse.ArgumentParser(prog='lojaintegrada_scripts', description='Scripts para manipular dados da Loja Integrada.')
  parser.add_argument('--data', '-d', help='Data no formado %d/%m/%Y')
  parser.add_argument('--range', '-r', nargs=2, help='Range de datas no formado %d/%m/%Y')
  parser.add_argument('--script', '-s', help='Script para ser executado', required=True)
  parser.add_argument("--mail_to", '-m', nargs="+", help="Lista de destinatários para enviar email")

  parser.add_argument("--log", '-l', help="Nível de verbosidade do log", 
                                     default='INFO', 
                                     choices=['debug', 'info', 'warning', 'error', 'critical'])

  return parser.parse_args()


def validate_args(args):
  datas = [datetime.today().strftime('%d/%m/%Y'), None]
  if args.range:
    datas = args.range
  elif args.data:
    datas = [args.data, None]

  try:
    datas = date_range(*datas)
  except:
    exit(1, "Data no formato inválido: a data deve estar no formato %d/%m/%Y\n")

  try:
    script = import_module(f'scripts.{args.script}')
  except:
    exit(1, f"Script não encontrado: {args.script}\n")

  return script, datas


def main():
  args = parse_args()
  
  logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%d/%m/%Y %H:%M', level=args.log.upper())
  logger = logging.getLogger(__name__)
  logger.debug(args)

  script, datas = validate_args(args)

  LI = LojaIntegrada(api_key=api_key, app_key=app_key)
  script.main(LI, datas, email_to=args.mail_to)
