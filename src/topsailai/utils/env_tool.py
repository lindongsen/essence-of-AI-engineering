'''
  Author: DawsonLin
  Email: lin_dongsen@126.com
  Created: 2025-10-27
  Purpose: Environment variable utilities and configuration helpers
'''

import os

def is_debug_mode():
    """Check if the application is running in debug mode.

    Debug mode is determined by the DEBUG environment variable:
    - DEBUG="0" or not set: Production mode (returns False)
    - DEBUG="1" or any other value: Debug mode (returns True)

    Returns:
        bool: True if debug mode is enabled, False otherwise
    """
    if os.getenv("DEBUG", "0") == "0":
        return False
    return True

def is_use_tool_calls() -> bool:
    """Check if tool calls functionality is enabled.

    Tool calls functionality is determined by the USE_TOOL_CALLS environment variable:
    - USE_TOOL_CALLS="0" or not set: Tool calls disabled (returns False)
    - USE_TOOL_CALLS="1" or any other value: Tool calls enabled (returns True)

    Returns:
        bool: True if tool calls are enabled, False otherwise
    """
    if os.getenv("USE_TOOL_CALLS", "0") == "0":
        return False
    return True

def is_chat_multi_line() -> bool:
    """Check if multi-line chat mode is enabled.

    Multi-line chat mode is determined by the CHAT_MULTI_LINE environment variable:
    - CHAT_MULTI_LINE="0" or not set: Single-line mode (returns False)
    - CHAT_MULTI_LINE="1" or any other value: Multi-line mode (returns True)

    Returns:
        bool: True if multi-line chat mode is enabled, False otherwise
    """
    if os.getenv("CHAT_MULTI_LINE", "0") == "0":
        return False
    return True


class EnvironmentReader(object):

    @staticmethod
    def try_read_file(file_path:str) -> str:
        """try to read

        Args:
            file_path (str): it may be not a file.
        """
        if not file_path:
            return ""
        if file_path[0] in "./" or len(file_path) <= 255:
            if os.path.exists(file_path):
                with open(file_path, encoding="utf-8") as fd:
                    return fd.read().strip()
        return ""

    @property
    def story_prompt_content(self):
        """ get content. the env_var may be a file or content. """
        env_var = os.getenv("STORY_PROMPT")
        if not env_var:
            return ""
        content = self.try_read_file(env_var)
        return content or env_var

    def get(self, name, default=None):
        return os.getenv(name, default=default)


# init
EnvReaderInstance = EnvironmentReader()
