# -*- coding: utf-8 -*-

from dotenv import load_dotenv
load_dotenv()

import argparse
import logging
from datetime import datetime, timedelta

import scripts
from plataformas import Plataforma
from helpers import date_range

logging.getLogger("urllib3.connectionpool").setLevel(logging.WARNING)


def parse_args():
  parser = argparse.ArgumentParser(prog='lojaintegrada_scripts', description='Scripts para manipular dados da Loja Integrada.')
  parser.add_argument('--data', '-d', help='Data no formado %d/%m/%Y')
  parser.add_argument('--range', '-r', nargs=2, help='Range de datas no formado %d/%m/%Y')
  parser.add_argument('--script', '-s', help='Script para ser executado', required=True)
  parser.add_argument("--mail_to", '-m', nargs="+", help="Lista de destinatários para enviar email")
  parser.add_argument("--pedido", '-p', help="Id do pedido")

  parser.add_argument("--log", '-l', help="Nível de verbosidade do log", 
                                     default='INFO', 
                                     choices=['debug', 'info', 'warning', 'error', 'critical'])

  return parser.parse_args()


def validate_args(args):
  datas = [(datetime.today() - timedelta(days=1)).strftime('%d/%m/%Y'), None]
  if args.range:
    datas = args.range
  elif args.data:
    datas = [args.data, None]

  try:
    datas = date_range(*datas)
  except:
    exit("Data no formato inválido: a data deve estar no formato %d/%m/%Y\n")

  try:
    ScriptClass = getattr(scripts, args.script)
  except:
    exit(f"Script não encontrado: {args.script}\n")

  return ScriptClass, datas


def script_orchestrator(scriptClass, datas, args):
  script_name = args.script.lower()

  if script_name == 'declaracao':
    script = scriptClass(Plataforma.get_plataforma('shopify'), args.pedido)
  elif script_name == 'pedidospagos':
    script = scriptClass(Plataforma.get_plataforma('lojaintegrada'), datas, email_to=args.mail_to)

  script()


def main():
  args = parse_args()
  
  logging.basicConfig(format='%(asctime)s - %(levelname)-8s - %(name)s - %(message)s', datefmt='%d/%m/%Y %H:%M', level=args.log.upper())
  logger = logging.getLogger(__name__)
  logger.debug(args)

  ScriptClass, datas = validate_args(args)

  script_orchestrator(ScriptClass, datas, args)
