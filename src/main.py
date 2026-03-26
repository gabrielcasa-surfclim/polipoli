import os
import time
import sys
import traceback
import requests

from telegram_bot import TelegramBot
from config import logger, SCAN_INTERVAL_SECONDS, HEARTBEAT_INTERVAL_HOURS


GAMMA_MARKETS_URL = "https://gamma-api.polymarket.com/markets"


def fetch_active_markets(limit: int = 10):
    response = requests.get(
        GAMMA_MARKETS_URL,
        params={
            "active": "true",
            "closed": "false",
            "limit": limit,
        },
        timeout=20,
    )
    response.raise_for_status()
    data = response.json()

    if not isinstance(data, list):
        return []

    markets = []
    for item in data[:limit]:
        question = item.get("question", "Sem pergunta")
        volume = item.get("volume", 0)
        slug = item.get("slug", "")
        markets.append({
            "question": question,
            "volume": volume,
            "slug": slug,
        })
    return markets


def format_markets_message(markets):
    if not markets:
        return "⚠️ Scanner online, mas não encontrou mercados ativos."

    lines = ["📊 Top mercados ativos no Polymarket:"]
    for i, market in enumerate(markets, start=1):
        lines.append(
            f"{i}. {market['question']} | volume: {market['volume']}"
        )
    return "\n".join(lines)


def main():
    bot = TelegramBot()
    bot.send("✅ Scanner Polymarket online no Render.")

    last_heartbeat = time.time()
    last_market_report = 0
    consecutive_errors = 0
    max_consecutive_errors = 5

    while True:
        try:
            now = time.time()

            if now - last_market_report > 3600:
                markets = fetch_active_markets(limit=10)
                message = format_markets_message(markets)
                bot.send(message)
                logger.info("Resumo de mercados enviado.")
                last_market_report = now

            if now - last_heartbeat > HEARTBEAT_INTERVAL_HOURS * 3600:
                bot.send("💚 Heartbeat: scanner ainda vivo.")
                logger.info("Heartbeat enviado.")
                last_heartbeat = now

            consecutive_errors = 0
            time.sleep(SCAN_INTERVAL_SECONDS)

        except Exception as e:
            consecutive_errors += 1
            logger.error(f"Erro no scanner: {e}")
            logger.error(traceback.format_exc())

            try:
                bot.send(f"⚠️ ERRO no scanner: {str(e)[:150]}")
            except Exception:
                pass

            if consecutive_errors >= max_consecutive_errors:
                try:
                    bot.send("🔥 CRÍTICO: muitos erros consecutivos. Reiniciando worker.")
                except Exception:
                    pass
                sys.exit(1)

            time.sleep(60)


if __name__ == "__main__":
    main()