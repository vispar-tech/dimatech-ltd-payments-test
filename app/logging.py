import inspect
import logging
import sys
from pathlib import Path

from loguru import logger

from app.settings import settings

CONSOLE_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
    "<level>{message}</level>"
)
FILE_FORMAT = (
    "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | "
    "{name}:{function}:{line} - {message}"
)


class InterceptHandler(logging.Handler):
    """
    Default handler from examples in loguru documentation.

    This handler intercepts all log requests and
    passes them to loguru.

    For more info see:
    https://loguru.readthedocs.io/en/stable/overview.html#entirely-compatible-with-standard-logging
    """

    def emit(self, record: logging.LogRecord) -> None:  # pragma: no cover
        """
        Propagates logs to loguru.

        :param record: record to log.
        """
        try:
            level: str | int = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        # Use inspect.stack() to properly determine the depth
        stack = inspect.stack()
        depth = 0
        logging_file = Path(logging.__file__).resolve() if logging.__file__ else None
        intercept_handler_file = Path(__file__).resolve()
        skipped_files = {logging_file, intercept_handler_file}

        # Walk up the stack to find the first frame outside of logging modules
        for frame_info in stack:
            frame_file = (
                Path(frame_info.filename).resolve() if frame_info.filename else None
            )

            # Skip frames from logging module and InterceptHandler
            if frame_file not in skipped_files and frame_info.function != "emit":
                break

            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level,
            record.getMessage(),
        )


def configure_logging() -> None:  # pragma: no cover
    """Configure logging."""
    intercept_handler = InterceptHandler()

    # Remove all existing handlers
    logger.remove()

    logger.add(
        sys.stdout,
        level=settings.log_level.value,
        format=CONSOLE_FORMAT,
        colorize=True,
    )

    # Configure file logging if enabled
    if settings.log_file_enabled:
        # Create log directory if it doesn't exist
        log_dir = Path(settings.log_dir)
        log_dir.mkdir(parents=True, exist_ok=True)

        # Main log file (all levels)
        logger.add(
            log_dir / "app.log",
            level=settings.log_level.value,
            format=FILE_FORMAT,
            rotation="10 MB",
            retention="30 days",
            compression="zip",
            encoding="utf-8",
            backtrace=True,
            diagnose=True,
        )

        # Error log file (ERROR and above only)
        logger.add(
            log_dir / "app_error.log",
            level="ERROR",
            format=FILE_FORMAT,
            rotation="10 MB",
            retention="30 days",
            compression="zip",
            encoding="utf-8",
            backtrace=True,
            diagnose=True,
        )

    # Configure standard logging to use InterceptHandler
    logging.basicConfig(handlers=[intercept_handler], level=logging.NOTSET)

    # Clear handlers for uvicorn loggers
    for logger_name in logging.root.manager.loggerDict:
        if logger_name.startswith("uvicorn."):
            logging.getLogger(logger_name).handlers = []

    # Change handler for default uvicorn logger
    logging.getLogger("uvicorn").handlers = [intercept_handler]
    logging.getLogger("uvicorn.access").handlers = [intercept_handler]
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)
