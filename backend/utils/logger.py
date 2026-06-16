import sys
from loguru import logger
logger.remove()

logger.add(
    sys.stdout,
    format=(
        "<green>{time:HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan> | "
        "<level>{message}</level>"
    ),
    level="DEBUG",
    colorize=True,
)

logger.add(
    "logs/chatbot.log",
    rotation="10 MB",      
    retention="7 days",     
    level="INFO",
    format="{time} | {level} | {name}:{function} | {message}",
)