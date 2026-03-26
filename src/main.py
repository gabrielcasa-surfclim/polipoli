import os
import sys
import time
import traceback
from typing import Callable, TypeVar

from dotenv import load_dotenv

from config import (
    HEARTBEAT_INTERVAL_HOURS,
    IS_RENDER,
    MAX_CONSECUTIVE_ERRORS,
    SCAN_INTERVAL_SECONDS,
    logger,
)
from telegram_bot import TelegramBot

T = TypeVar("T")


if not IS_RENDER:
    load_dotenv()


def run_with_backoff(func: Callable[[], T], max_retries: int = 5) -> T:
    last_error: Exception | None = None
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as exc:  # pragma: no cover
            last_error = exc
            wait_seconds = 2 ** attempt
            logger.warning(
                "Falha na execução (tentativa %s/%s): %s. Aguardando %ss.",
                attempt + 1,
                max_retries,
                exc,
                wait_seconds,
            )
            time.sleep(wait_seconds)
    raise RuntimeError(f"Falha após {max_retries} tentativas: {last_error}")


def example_scanner_cycle() -> None:
    """Ponto de entrada do scanner real futuramente.

    Hoje ele apenas registra um log de ciclo para confirmar que o worker está vivo.
    """
    logger.info("Ciclo do scanner executado.")


def main() -> None:
    bot = TelegramBot()
    run_with_backoff(lambda: bot.send("✅ <b>Scanner iniciado no Render.</b>"))

    last_heartbeat = time.time()
    consecutive_errors = 0

    logger.info("Worker iniciado. Ambiente Render=%s", IS_RENDER)

    while True:
        try:
            run_with_backoff(example_scanner_cycle)

            now = time.time()
            if now - last_heartbeat >= HEARTBEAT_INTERVAL_HOURS * 3600:
                message = "💚 <b>Heartbeat:</b> scanner ainda vivo."
                run_with_backoff(lambda: bot.send(message))
                last_heartbeat = now
                logger.info("Heartbeat enviado.")

            consecutive_errors = 0
            time.sleep(SCAN_INTERVAL_SECONDS)

        except Exception as exc:
            consecutive_errors += 1
            trace = traceback.format_exc()
            logger.error("Erro no scanner (%s/%s): %s\n%s", consecutive_errors, MAX_CONSECUTIVE_ERRORS, exc, trace)

            try:
                bot.send(f"⚠️ <b>Erro no scanner</b>: {str(exc)[:300]}")
            except Exception:
                logger.exception("Falha ao enviar alerta de erro no Telegram.")

            if consecutive_errors >= MAX_CONSECUTIVE_ERRORS:
                try:
                    bot.send("🔥 <b>Crítico:</b> múltiplos erros consecutivos. Encerrando para o Render reiniciar.")
                except Exception:
                    logger.exception("Falha ao enviar alerta crítico no Telegram.")

                logger.critical("Encerrando processo para reinício automático pelo Render.")
                sys.exit(1)

            time.sleep(min(60, SCAN_INTERVAL_SECONDS * 2))


if __name__ == "__main__":
    if not os.getenv("TELEGRAM_BOT_TOKEN") or not os.getenv("TELEGRAM_CHAT_ID"):
        logger.warning("Variáveis TELEGRAM_BOT_TOKEN e/ou TELEGRAM_CHAT_ID ausentes.")
    main()
