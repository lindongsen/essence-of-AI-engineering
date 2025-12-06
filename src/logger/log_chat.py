'''
  Author: DawsonLin
  Email: lin_dongsen@126.com
  Created: 2025-10-20
  Purpose:
'''

from .base_logger import setup_logger

LOGGER_NAME = "chat"

logger = setup_logger(LOGGER_NAME, None)
