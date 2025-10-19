'''
  Author: DawsonLin
  Email: lin_dongsen@126.com
  Created: 2025-10-18
  Purpose:
'''

import os


def get_all_agent_tools():
    """ return dict, key is tool_name, value is tool_func. """
    from . import TOOLS as INTERNAL_TOOLS

    agent_tools = {}
    for tool_name, tool_func in INTERNAL_TOOLS.items():
        if tool_name.startswith("agent"):
            agent_tools[tool_name] = tool_func
    return agent_tools

def agent_writer(msg_or_file:str, model_name:str=None):
    """ A professional Assistant for writer.

    # parameters
    :msg_or_file: string, can be message or file path.
        if user pass a file path, the content of the file will be read as message.
        if the user does explicitly specify a file, should use it directly.

    :model_name: If the user does not explicitly specify, this parameter is not needed.

    # return
    return final answer.
    """
    message = msg_or_file
    # read message from file if msg_or_file is a file path
    if msg_or_file[0] in ["/", "."]:
        if os.path.isfile(msg_or_file):
            with open(msg_or_file, "r", encoding="utf-8") as f:
                message = f.read()

    from ai_base.agent_base import AgentRun
    from AgentReAct import SYSTEM_PROMPT, Step4ReAct

    agent = AgentRun(
        system_prompt=SYSTEM_PROMPT + "\nYou are a professional writer.\n",
        tools=None,
        agent_name="AgentWriter",
        excluded_tool_kits=get_all_agent_tools().keys(),
    )
    if not model_name:
        model_name = "DeepSeek-V3.1"
    agent.llm_model.openai_model_name = model_name
    return agent.run(Step4ReAct(), message)

def agent_programmer(msg_or_file:str, model_name:str=None):
    """ A professional Assistant for programmer.

    # parameters
    :msg_or_file: string, can be message or file path.
        if user pass a file path, the content of the file will be read as message.
        if the user does explicitly specify a file, should use it directly.

    :model_name: If the user does not explicitly specify, this parameter is not needed.

    # return
    return final answer.
    """
    message = msg_or_file
    # read message from file if msg_or_file is a file path
    if msg_or_file[0] in ["/", "."]:
        if os.path.isfile(msg_or_file):
            with open(msg_or_file, "r", encoding="utf-8") as f:
                message = f.read()

    from ai_base.agent_base import AgentRun
    from AgentReAct import SYSTEM_PROMPT, Step4ReAct
    agent = AgentRun(
        system_prompt=SYSTEM_PROMPT + "\nYou are a professional programmer.\n",
        tools=None,
        agent_name="AgentProgrammer",
        excluded_tool_kits=get_all_agent_tools().keys(),
    )
    if not model_name:
        model_name = "DeepSeek-V3.1"
    agent.llm_model.openai_model_name = model_name
    return agent.run(Step4ReAct(), message)


TOOLS = dict(
    agent_writer=agent_writer,
    agent_programmer=agent_programmer,
)
