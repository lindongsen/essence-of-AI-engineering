'''
  Author: DawsonLin
  Email: lin_dongsen@126.com
  Created: 2025-10-18
  Purpose:
'''
from logger.log_chat import logger
from tools import get_tool_prompt
from ai_base.constants import (
    ROLE_USER, ROLE_ASSISTANT, ROLE_SYSTEM, ROLE_TOOL,
)
from utils.print_tool import (
    print_step,
    print_error,
)
from utils.json_tool import (
    to_json_str,
    json_load,
)
from utils import time_tool
from utils.thread_local_tool import (
    get_agent_name,
)

class PromptBase(object):
    """ prompt base manager """

    # define flags
    flag_dump_messages = False

    def __init__(self, system_prompt:str, tool_prompt:str="", tools_name:list=None):
        assert system_prompt, "missing system_prompt"
        self.system_prompt = system_prompt
        self.tool_prompt = tool_prompt or ""
        if tools_name:
            self.tool_prompt += get_tool_prompt(tools_name)

        # debug
        if self.tool_prompt:
            print_step(f"[tool_prompt]:\n{self.tool_prompt}\n")

        # context messages
        self.messages = []
        self.reset_messages(to_suppress_log=True)

    def append_message(self, msg:dict, to_suppress_log=False):
        """ append a message to context """
        if not to_suppress_log:
            logger.info(msg)
        self.messages.append(msg)

    def init_prompt(self):
        """ init sth. """
        self.reset_messages()

    def new_session(self, user_message):
        """ start a new session """
        self.init_prompt()
        self.add_user_message(user_message)

    def hook_format_content(self, content):
        """ set a hook to format content to text for LLM can to read """
        return to_json_str(content)

    def reset_messages(self, to_suppress_log=False):
        """ reset context message. clear all of messages. """
        self.messages = []
        self.append_message({"role": ROLE_SYSTEM, "content": self.system_prompt}, to_suppress_log)
        if self.tool_prompt:
            self.append_message({"role": ROLE_SYSTEM, "content": self.tool_prompt}, to_suppress_log)

    def add_user_message(self, content):
        """ the message from human """
        if content is None:
            return
        content = self.hook_format_content(content)
        print_step(content)
        self.append_message({"role": ROLE_USER, "content": content})

    def add_assistant_message(self, content):
        """ the message from LLM """
        if content is None:
            return
        content = self.hook_format_content(content)
        print_step(content)
        self.append_message({"role": ROLE_ASSISTANT, "content": content})

    def add_tool_message(self, content):
        """ the message from tool call """
        if content is None:
            return
        content = self.hook_format_content(content)
        print_step(content)
        self.append_message({"role": ROLE_TOOL, "content": content})

    def dump_messages(self):
        """ dump messages to a file.

        return file path. None for failed.
        """
        try:
            now_date = time_tool.get_current_date(True)
            file_name = f"{get_agent_name()}.{now_date}.msg"
            file_path = file_name
            with open(file_path, 'w', encoding='utf-8') as fd:
                fd.write(to_json_str(self.messages))
            print_step(f"dump messages: [{file_path}]")
            return file_path
        except Exception as e:
            print_error(f"dump messages failed: {e}")
        return None

    def load_messages(self, file_path:str):
        """ read file content as messages """
        with open(file_path, encoding='utf-8') as fd:
            content = fd.read()
            self.messages = json_load(content)
            assert isinstance(self.messages, list)
        return
