'''
  Author: DawsonLin
  Email: lin_dongsen@126.com
  Created: 2025-10-20
  Purpose:
'''

from utils import print_tool

MAX_MSG_SIZE = 3000

def truncate_message(msg:str):
    """
    max_msg_size: 1000
    """
    suffix = ""
    if len(msg) > MAX_MSG_SIZE:
        print_tool.print_error(f"truncate message with the size: [{MAX_MSG_SIZE}]")
        suffix = " ... (force to truncate)"

    return msg[:MAX_MSG_SIZE] + suffix
