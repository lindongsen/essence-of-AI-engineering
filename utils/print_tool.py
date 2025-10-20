import os
from datetime import datetime

from utils import thread_local_tool
from logger.log_chat import logger

g_flag_print_step = None

def enable_flag_print_step():
    global g_flag_print_step
    g_flag_print_step = True

def disable_flag_print_step():
    global g_flag_print_step
    g_flag_print_step = False

def print_with_time(msg):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    content = (f"[{now}] {msg}")
    agent_name = thread_local_tool.get_thread_var(thread_local_tool.KEY_AGENT_NAME)
    if agent_name:
        content = f"[{agent_name}] " + content
    print(content)

def print_step(msg):
    if g_flag_print_step is False:
        return
    if os.getenv("DEBUG", "0") == "1" or g_flag_print_step:
        print_with_time(msg)
    return

def print_error(msg):
    logger.error(msg)
    print_with_time(f"Error: {msg}")
    return
