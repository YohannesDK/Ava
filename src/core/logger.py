import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


PROJECT_ROOT = Path(__file__).parent.parent.parent
LOGS_DIR = PROJECT_ROOT / "logs"


class FlushLogger:
    def __init__(self, logger: logging.Logger):
        self.logger = logger
    
    def _flush(self):
        sys.stdout.flush()
        sys.stderr.flush()
    
    def info(self, message: str):
        self.logger.info(message)
        self._flush()
    
    def error(self, message: str):
        self.logger.error(message)
        self._flush()
    
    def warning(self, message: str):
        self.logger.warning(message)
        self._flush()
    
    def debug(self, message: str):
        self.logger.debug(message)
        self._flush()


_logger: Optional[FlushLogger] = None
_log_file_path: Optional[Path] = None


def init_logging(personality: str = "default") -> FlushLogger:
    global _logger, _log_file_path
    
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
    log_filename = f"{timestamp}-{personality}.log"
    log_path = LOGS_DIR / log_filename
    _log_file_path = log_path
    
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(log_path, mode="a"),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logger = logging.getLogger("ava")
    _logger = FlushLogger(logger)
    
    return _logger


def get_logger() -> FlushLogger:
    global _logger
    if _logger is None:
        _logger = init_logging()
    return _logger


def log_config(config: dict):
    logger = get_logger()
    logger.info("=" * 50)
    logger.info("Ava Configuration")
    logger.info("=" * 50)
    for key, value in config.items():
        logger.info(f"  {key}: {value}")
    logger.info("=" * 50)


def log_error(error: Exception, context: str = ""):
    logger = get_logger()
    error_msg = f"ERROR"
    if context:
        error_msg += f" in {context}"
    error_msg += f": {type(error).__name__}: {str(error)}"
    logger.error(error_msg)


def log_message(role: str, content: str, max_length: int = 100):
    logger = get_logger()
    if len(content) > max_length:
        content = content[:max_length] + "..."
    logger.debug(f"[{role.upper()}] {content}")


def get_log_file_path() -> Optional[Path]:
    return _log_file_path
