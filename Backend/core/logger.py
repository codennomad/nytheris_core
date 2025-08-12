import sys
from loguru import logger


logger.remove()

logger.add(
    sys.stderr,
    level="INFO",
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    colorize=True
)

logger.add(
    "logs/error.log",
    level="ERROR",
    rotation="25 MB"
    retention="15 days"
    format="{time} {level} {message}",
    serialize=True
)

log = logger