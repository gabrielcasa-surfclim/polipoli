# Polymarket IDS Scanner

Scaffold inicial para rodar um worker 24/7 no Render com alertas no Telegram.

## Estrutura

- `src/main.py`: loop principal com heartbeat, backoff e reinício em caso de falhas consecutivas.
- `src/telegram_bot.py`: envio de mensagens no Telegram com rate limit simples.
- `src/config.py`: configuração centralizada.
- `render.yaml`: deploy como background worker no Render.
- `.env.example`: variáveis de ambiente para uso local.

## Rodando localmente

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python src/main.py
```

## Deploy no Render

1. Suba o projeto para um repositório no GitHub.
2. No Render, crie um serviço do tipo **Background Worker**.
3. Configure as env vars obrigatórias:
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`
4. Use `python src/main.py` como start command.

## Próximo passo

Substituir a função `example_scanner_cycle()` pela lógica real de:
- discovery de mercados na Gamma API
- leitura de book/trades
- cálculo do IDS
- envio de alertas condicionais
