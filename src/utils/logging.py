import logging
import os
from logging.handlers import RotatingFileHandler

from rich.logging import RichHandler


def setup_logging(log_level=logging.INFO, log_file="saa_orchestrator.log"):
    # Create logs directory if it doesn't exist
    logs_dir = os.path.join(os.getcwd(), "logs")
    os.makedirs(logs_dir, exist_ok=True)

    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            RichHandler(rich_tracebacks=True),
            RotatingFileHandler(
                os.path.join(logs_dir, log_file),
                maxBytes=10_000_000,  # 10MB
                backupCount=5,
            ),
        ],
    )

    # Create a logger for this module
    logger = logging.getLogger(__name__)

    return logger


# Usage example
logger = setup_logging()
