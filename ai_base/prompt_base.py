'''
  Author: DawsonLin
  Email: lin_dongsen@126.com
  Created: 2025-10-18
  Purpose:
'''

from tools import get_tool_prompt
from ai_base.constants import (
    ROLE_USER, ROLE_ASSISTANT, ROLE_SYSTEM, ROLE_TOOL,
)
from utils.print_tool import (
    print_step,
)
from utils.json_tool import (
    to_json_str,
)

class PromptBase(object):
    """ prompt base manager """
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
        self.reset_messages()

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

    def reset_messages(self):
        """ reset context message. clear all of messages. """
        self.messages = []
        self.messages.append({"role": ROLE_SYSTEM, "content": self.system_prompt})
        if self.tool_prompt:
            self.messages.append({"role": ROLE_SYSTEM, "content": self.tool_prompt})

    def add_user_message(self, content):
        """ the message from human """
        if content is None:
            return
        content = self.hook_format_content(content)
        print_step(content)
        self.messages.append({"role": ROLE_USER, "content": content})

    def add_assistant_message(self, content):
        """ the message from LLM """
        if content is None:
            return
        content = self.hook_format_content(content)
        print_step(content)
        self.messages.append({"role": ROLE_ASSISTANT, "content": content})

    def add_tool_message(self, content):
        """ the message from tool call """
        if content is None:
            return
        content = self.hook_format_content(content)
        print_step(content)
        self.messages.append({"role": ROLE_TOOL, "content": content})
