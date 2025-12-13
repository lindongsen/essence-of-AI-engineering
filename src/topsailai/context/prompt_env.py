'''
  Author: DawsonLin
  Email: lin_dongsen@126.com
  Created: 2025-12-11
  Purpose:
'''
import os

from topsailai.utils import (
    time_tool,
    cmd_tool,
)


def get_system_info() -> dict:
    """ system key info """
    result = {}

    ret = cmd_tool.exec_cmd("uname -a")
    if ret and ret[1]:
        result["uname"] = ret[1].strip()

    if os.path.exists("/etc/issue"):
        with open("/etc/issue", encoding="utf-8") as fd:
            result["issue"] = fd.read().strip()

    return result


class _Base(object):
    def __init__(self):
        pass

    def __str__(self):
        return self.prompt

    @property
    def prompt(self) -> str:
        """ return prompt """
        raise NotImplementedError


class CurrentDate(_Base):
    """ prompt about of current date """
    @property
    def prompt(self) -> str:
        """ return date info """
        return f"""CurrentDate: {time_tool.get_current_date(True)}"""

class CurrentSystem(_Base):
    """ system info """
    system_info = get_system_info()

    @property
    def prompt(self) -> str:
        """ return system info """
        result = "System Info:\n"
        for k, v in self.system_info.items():
            if v:
                result += f"- {k}:{v}\n"
        return result

def generate_prompt_for_env() -> str:
    """ return env info """

    env_prompt = os.getenv("ENV_PROMPT") or ""
    if env_prompt:
        # Dynamically retrieve file content
        if env_prompt[0] in ['.', '/']:
            with open(env_prompt, encoding="utf-8") as fd:
                env_prompt = fd.read()

    return "# Environment\n" + "\n".join(
        [
            CurrentDate().prompt,
            CurrentSystem().prompt,
            env_prompt,
        ]
    )
