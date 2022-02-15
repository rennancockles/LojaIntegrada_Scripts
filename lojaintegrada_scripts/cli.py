# -*- coding: utf-8 -*-

import logging
from enum import Enum
from typing import Optional

import typer
from dotenv import load_dotenv

load_dotenv()

from commands import Declaracao, PedidosEnviados, PedidosPagos  # noqa: E402
from helpers import format_dates  # noqa: E402
from plataformas import Plataforma  # noqa: E402

logging.getLogger("urllib3.connectionpool").setLevel(logging.WARNING)
app = typer.Typer(
    name="lojaintegrada_scripts",
    help="Scripts para manipular dados da Loja Integrada.",
)
logger: logging.Logger


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
    logger.debug("Running script: declaracao")
    logger.debug(f"{pedido = }")

    script = Declaracao(
        plataforma=Plataforma.get_plataforma("shopify"), pedido_id=int(pedido)
    )
    script.run()


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
    logger.debug("Running script: pedidos_pagos")
    logger.debug(f"{date = }, {range = }, {mail_to = }")

    try:
        dates = format_dates(date, range)
    except Exception as e:
        logger.debug(f"Exception: {e}")
        typer.echo("Data no formato inválido: a data deve estar no formato %d/%m/%Y")
        raise typer.Exit(code=1)

    script = PedidosPagos(
        plataforma=Plataforma.get_plataforma("lojaintegrada"),
        datas=dates,
        email_to=mail_to,
    )
    script.run()


@app.command()
def pedidos_enviados(
    mail_to: list[str] = typer.Option(
        ...,
        "--mail_to",
        "-m",
        help="Lista de destinatários para enviar email",
    ),
) -> None:
    logger.debug("Running script: pedidos_enviados")
    logger.debug(f"{mail_to = }")

    script = PedidosEnviados(
        plataforma=Plataforma.get_plataforma("lojaintegrada"), email_to=mail_to
    )
    script.run()


@app.callback()
def callback(
    ctx: typer.Context,
    log: LogLevel = typer.Option(
        LogLevel.info,
        "--log",
        "-l",
        help="Nível de verbosidade do log",
        case_sensitive=False,
    ),
) -> None:
    global logger

    logging.basicConfig(
        format="%(asctime)s - %(levelname)-8s - %(name)s - %(message)s",
        datefmt="%d/%m/%Y %H:%M",
        level=log.value,
    )
    logger = logging.getLogger(__name__)
    logger.info(f"Executando comando {ctx.invoked_subcommand}")


if __name__ == "__main__":
    app()
