# -*- coding: utf-8 -*-

from typing import Optional
from dotenv import load_dotenv
load_dotenv()

from enum import Enum
import logging

import typer

from scripts import declaracao, pedidosPagosCompleto, pedidosEnviados
from plataformas import Plataforma
from helpers import format_dates

logging.getLogger("urllib3.connectionpool").setLevel(logging.WARNING)
app = typer.Typer(
    name="lojaintegrada_scripts",
    help="Scripts para manipular dados da Loja Integrada.",
)


class LogLevel(str, Enum):
    debug = "DEBUG"
    info = "INFO"
    warning = "WARNING"
    error = "ERROR"
    critical = "CRITICAL"


@app.command()
def declaracao(
    pedido: str = typer.Option(
        ...,
        "--pedido",
        "-p",
        help="Id do pedido",
    ),
) -> None:
    typer.echo("Executando script: declaracao")
    typer.echo(f"{pedido = }")
    declaracao(Plataforma.get_plataforma('shopify'), pedido)()


@app.command()
def pedidos_pagos(
    date: Optional[str] = typer.Option(
        None,
        "--date",
        "-d",
        help="Data no formado %d/%m/%Y",
    ),
    range: Optional[tuple[str, str]] = typer.Option(
        None,
        "--range",
        "-r",
        help="Range de datas no formado %d/%m/%Y",
    ),
    mail_to: list[str] = typer.Option(
        ...,
        "--mail_to",
        "-m",
        help="Lista de destinatários para enviar email",
    ),
) -> None:

    typer.echo("Executando script: pedidos_pagos")
    typer.echo(f"{date = }")
    typer.echo(f"{range = }")
    typer.echo(f"{mail_to = }")

    try:
        dates = format_dates(date, range)
    except:
        typer.echo("Data no formato inválido: a data deve estar no formato %d/%m/%Y")
        raise typer.Exit(code=1)

    typer.echo(f"{dates = }")
    pedidosPagosCompleto(Plataforma.get_plataforma('lojaintegrada'), dates, email_to=mail_to)()


@app.command()
def pedidos_enviados(
    mail_to: list[str] = typer.Option(
        ...,
        "--mail_to",
        "-m",
        help="Lista de destinatários para enviar email",
    ),
) -> None:
    typer.echo("Executando script: pedidos_enviados")
    typer.echo(f"{mail_to = }")
    pedidosEnviados(Plataforma.get_plataforma('lojaintegrada'), email_to=mail_to)()


@app.callback()
def callback(
    ctx: typer.Context,
    log: LogLevel = typer.Option(
        LogLevel.info,
        "--log",
        "-l",
        help="Nível de verbosidade do log",
        case_sensitive=False
    )
) -> None:
    logging.basicConfig(
      format="%(asctime)s - %(levelname)-8s - %(name)s - %(message)s",
      datefmt="%d/%m/%Y %H:%M",
      level=log.value
    )
    logger = logging.getLogger(__name__)
    logger.info(f"Executando comando {ctx.invoked_subcommand}")


if __name__ == "__main__":
    app()