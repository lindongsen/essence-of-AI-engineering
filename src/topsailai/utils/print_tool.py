import os
from datetime import datetime

from topsailai.logger.log_chat import logger

from . import thread_local_tool


g_flag_print_step = None

def enable_flag_print_step():
    """Enable step-by-step printing for debugging purposes.

    When enabled, print_step() calls will output messages with timestamps.
    This is useful for tracking the execution flow during development.
    """
    global g_flag_print_step
    g_flag_print_step = True

def disable_flag_print_step():
    """Disable step-by-step printing.

    When disabled, print_step() calls will not output any messages.
    """
    global g_flag_print_step
    g_flag_print_step = False

def print_with_time(msg):
    """Print a message with a timestamp and optional agent name prefix.

    Args:
        msg: Message string to print

    The output format includes:
    - Current timestamp in YYYY-MM-DD HH:MM:SS format
    - Optional agent name if set in thread-local storage
    - The message content
    """
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    content = (f"[{now}] {msg}")
    agent_name = thread_local_tool.get_thread_var(thread_local_tool.KEY_AGENT_NAME)
    if agent_name:
        content = f"[{agent_name}] " + content
    print(content)

def print_step(msg):
    """Print a step message if step printing is enabled.

    This function only prints messages when:
    - DEBUG environment variable is set to "1"
    - OR g_flag_print_step is explicitly enabled

    Args:
        msg: Step message to print
    """
    if g_flag_print_step is False:
        return
    if os.getenv("DEBUG", "0") == "1" or g_flag_print_step:
        print_with_time(msg)
    return

def print_error(msg):
    """Print an error message to both logger and console.

    This function logs the error using the application's logger
    and also prints it to the console with a timestamp.

    Args:
        msg: Error message to log and print
    """
    logger.error(msg)
    print_with_time(f"Error: {msg}")
    return
