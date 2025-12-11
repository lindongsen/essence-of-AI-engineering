'''
  Author: DawsonLin
  Email: lin_dongsen@126.com
  Created: 2025-10-20
  Purpose:
'''

from topsailai.utils import print_tool
from topsailai.utils.thread_local_tool import get_agent_name

MAX_MSG_SIZE = 3000
LARGE_MSG_SIZE = 13000

def is_need_truncate(msg_len:int):
    """ return bool. True is need truncate. """
    if get_agent_name() == "AgentWriter":
        if msg_len > LARGE_MSG_SIZE:
            return True
        return False
    if msg_len >= MAX_MSG_SIZE:
        return True
    return False

def truncate_message(msg):
    """ force to truncate message by the max_msg_size """
    suffix = ""
    if is_need_truncate(len(msg)):
        print_tool.print_error(f"truncate message with the size: [{MAX_MSG_SIZE}]")
        suffix = " ... (force to truncate)"

    if isinstance(msg, bytes):
        if suffix:
            suffix = bytes(suffix, "utf-8")
        else:
            suffix = b""

    return msg[:MAX_MSG_SIZE] + suffix
