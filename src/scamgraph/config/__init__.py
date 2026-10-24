"""
ScamGraph AI - Configuration Package
"""

from scamgraph.config.config import Config, config
from scamgraph.config.logging import get_logger, setup_logging

__all__ = ["Config", "config", "get_logger", "setup_logging"]