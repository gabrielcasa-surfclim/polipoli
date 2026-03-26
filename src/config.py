import logging
import os

# Configuração de logging
logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper(), logging.INFO),
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Configurações do scanner
SCAN_INTERVAL_SECONDS = int(os.getenv("SCAN_INTERVAL", "30"))
HEARTBEAT_INTERVAL_HOURS = int(os.getenv("HEARTBEAT_HOURS", "6"))
MAX_CONSECUTIVE_ERRORS = int(os.getenv("MAX_CONSECUTIVE_ERRORS", "5"))
IDS_THRESHOLD = int(os.getenv("IDS_THRESHOLD", "70"))

# URLs base (para próximas etapas)
POLYMARKET_GAMMA_API = os.getenv("POLYMARKET_GAMMA_API", "https://gamma-api.polymarket.com")
POLYMARKET_CLOB_API = os.getenv("POLYMARKET_CLOB_API", "https://clob.polymarket.com")

# Render define algumas env vars. Se existir, assumimos ambiente de produção.
IS_RENDER = bool(os.getenv("RENDER") or os.getenv("RENDER_SERVICE_ID"))
