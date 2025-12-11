'''
  Author: DawsonLin
  Email: lin_dongsen@126.com
  Created: 2025-10-29
  Purpose:
'''

import os
from topsailai.utils import module_tool

ALL_MANAGERS = module_tool.get_function_map(
    "topsailai.context.chat_history_manager",
    "MANAGERS",
)
