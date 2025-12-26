import os
from datetime import datetime
import simplejson

from topsailai.logger.log_chat import logger
from topsailai.utils import thread_local_tool


g_flag_print_step = None

def get_truncation_len() -> int|None:
    """Get the truncation length for debug printing from environment.

    Returns:
        int|None: Truncation length as integer if DEBUG_PRINT_TRUNCATE_LENGTH is set,
                 otherwise None.
    """
    truncation_len = os.getenv("DEBUG_PRINT_TRUNCATE_LENGTH")
    try:
        if truncation_len:
            return int(truncation_len)
    except Exception:
        pass
    return None

def truncate_msg(msg:str|list|dict, key_name="step_name", value_name="raw_text") -> str:
    """Truncate message content if it exceeds configured length.

    Args:
        msg (str|list|dict): Message to truncate. If string length exceeds limit,
                              it may be parsed as JSON for structured truncation.
        key_name (str): Key name for structured messages (default: "step_name").
        value_name (str): Value name for structured messages (default: "raw_text").

    Returns:
        str: Truncated message as string (possibly JSON).
    """
    from topsailai.utils import json_tool
    from .format_tool import to_list

    truncation_len = get_truncation_len()
    if truncation_len and truncation_len > 0:
        if isinstance(msg, str) and len(msg) > (truncation_len + 100):
            msg = json_tool.json_load(msg)

        if isinstance(msg, (dict, list)):
            for _msg_d in to_list(msg):
                _raw_text = _msg_d.get(value_name)
                if _raw_text and len(_raw_text) > truncation_len:
                    _msg_d[value_name] = _msg_d[value_name][:truncation_len] + f" (truncated) ... total_len={len(_raw_text)} tail_content=[{_raw_text[-30:]}]"

            msg = json_tool.json_dump(msg, indent=2)

    return msg

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
    from . import thread_local_tool, format_tool

    try:
        msg = truncate_msg(msg)
        msg = format_tool.to_topsailai_format(
            msg, key_name="step_name", value_name="raw_text",
            for_print=True,
        ).strip()
    except Exception as e:
        # debug
        logger.exception("fail to format message: [>>>%s<<<], e=[%s]", msg, e)
        pass

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
    if thread_local_tool.get_thread_var(
        thread_local_tool.KEY_FLAG_DEBUG
    ) == 0:
        return
    if g_flag_print_step is False:
        return
    if os.getenv("DEBUG", "0") == "1" or g_flag_print_step:
        print_with_time(msg)
    return

def print_debug(msg):
    """Print a debug message with step printing enabled.

    Args:
        msg: Debug message to print.
    """
    msg = f"[DEBUG] {msg}"
    print_step(msg)

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

def format_dict_to_md(d:dict) -> str:
    """Make content easier to read

    Args:
        d (dict):

    Returns:
        str:
    """
    s = ""
    for k, v in d.items():
        s += f"\n## {k}\n"
        s += "```\n"
        if isinstance(v, str):
            s += v.strip()
        else:
            s += simplejson.dumps(v, indent=2, ensure_ascii=False)
        s += "\n```\n"
    return s
