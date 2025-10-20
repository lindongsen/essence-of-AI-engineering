'''
  Author: DawsonLin
  Email: lin_dongsen@126.com
  Created: 2025-10-20
  Purpose:
'''

import os
import logging
from logging.handlers import RotatingFileHandler

LOGGER_NAME = "chat"


class AgentFormatter(logging.Formatter):
    def __init__(self, fmt=None, datefmt=None):
        logging.Formatter.__init__(self, fmt, datefmt)

    def format(self, record):
        from utils.thread_local_tool import get_agent_name
        # thread local in python
        agent_name = get_agent_name()
        if not agent_name:
            # env in script
            agent_name = os.environ.get("AGENT_NAME", "") or os.environ.get("AI_AGENT", "")
        if agent_name:
          agent_name = f"({agent_name})"
        record.agent_name = agent_name or ""
        return logging.Formatter.format(self, record)


def __gen_logger():
    """ generate logger """
    formatter = AgentFormatter('%(asctime)s %(levelname)s -%(thread)d- %(message)s (%(pathname)s:%(lineno)d)%(agent_name)s')
    root_logger = logging.getLogger()

    log_file = LOGGER_NAME + ".log"
    file_handler = RotatingFileHandler(log_file, maxBytes=100000000, backupCount=1)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    curr_logger = logging.getLogger(LOGGER_NAME)
    curr_logger.setLevel(logging.DEBUG)
    return curr_logger

logger = __gen_logger()
