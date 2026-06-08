import logging
import sys


def configure_logging() -> None:
    """
    Basic structured logging setup.

    This keeps logs readable during development and useful later for Render.
    """
    logging.basicConfig(
        level=logging.INFO,
        format=(
            "%(asctime)s | %(levelname)s | %(name)s | "
            "%(filename)s:%(lineno)d | %(message)s"
        ),
        handlers=[logging.StreamHandler(sys.stdout)],
    )