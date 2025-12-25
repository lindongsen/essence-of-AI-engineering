#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
  Author: DawsonLin
  Email: lin_dongsen@126.com
  Created: 2025-10-19
  Purpose:
  Env:
    @SESSION_ID: string;
    @SYSTEM_PROMPT: file or content;
'''

import os
import sys
# DONOT DELETE THIS FOR FUNCTION 'input'
import readline
from dotenv import load_dotenv

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root + "/src")

os.chdir(project_root)

from topsailai.ai_base.agent_base import AgentRun
from topsailai.ai_base.agent_types import react
from topsailai.context import ctx_manager
from topsailai.utils import (
    env_tool,
)
from topsailai.utils.input_tool import get_message, input_message
from topsailai.workspace.hook_instruction import HookInstruction
from topsailai.tools.agent_tool import async_agent_memory_as_story


def get_agent(system_prompt="", to_dump_messages=False):
    """ return a agent object. """
    agent = AgentRun(
        react.SYSTEM_PROMPT + "\n====\n" + system_prompt,
        tools=None,
        agent_name=react.AGENT_NAME,
        excluded_tool_kits=["agent_tool"]
    )

    # set flags
    if to_dump_messages:
        agent.flag_dump_messages = True

    return agent


def main():
    """ main entry """
    load_dotenv()

    message = get_message()

    # session
    session_id = os.getenv("SESSION_ID")
    messages_from_session = None
    if session_id:
        print(f"session_id: {session_id}")

        messages_from_session = ctx_manager.get_messages_by_session(session_id)
        if not messages_from_session:
            ctx_manager.create_session(session_id, task=message)

    # system prompt
    env_sys_prompt = os.getenv("SYSTEM_PROMPT")
    sys_prompt_file = ""
    sys_prompt_content = ""
    if env_sys_prompt:
        if os.path.exists(env_sys_prompt):
            sys_prompt_file = env_sys_prompt
        else:
            sys_prompt_content = env_sys_prompt

    if sys_prompt_file:
        with open(sys_prompt_file, encoding="utf-8") as fd:
            sys_prompt_content = fd.read().strip()

    # agent
    agent = get_agent(sys_prompt_content)

    # llm
    llm_model = agent.llm_model
    llm_model.max_tokens = max(1600, llm_model.max_tokens)
    llm_model.temperature = max(0.97, llm_model.temperature)

    if not messages_from_session:
        messages_from_session = []

    def add_session_message():
        if session_id:
            ctx_manager.add_session_message(session_id, agent.messages[-1])
        messages_from_session.append(agent.messages[-1])

    def hook_after_init_prompt(self):
        if messages_from_session:
            self.messages += messages_from_session

    def hook_after_new_session(self):
        add_session_message()

    agent.hooks_after_init_prompt.append(hook_after_init_prompt)
    agent.hooks_after_new_session.append(hook_after_new_session)

    hook_instruction = HookInstruction()
    def _clear():
        if session_id:
            print(f"{message}: Context cannot be clear due to exist session_id({session_id})")
        else:
            # clear context messages
            messages_from_session = []
            print("/clear: Context already is clear")
        return
    def _story():
        if not messages_from_session:
            return
        async_agent_memory_as_story(messages_from_session)
        print("/story: The history messages will be save to a new story")
        return
    hook_instruction.add_hook("/clear", _clear)
    hook_instruction.add_hook("/story", _story)

    max_count = 100
    while True:
        max_count -= 1
        answer = agent.run(react.Step4ReAct(True), message)
        if answer:
            add_session_message()

        if not env_tool.is_debug_mode():
            print()
            print(">>> answer:")
            print(answer)

        print()
        if max_count == 0:
            break

        while True:
            message = input_message()

            message = message.strip()
            if hook_instruction.exist_hook(message):
                hook_instruction.call_hook(message)
                continue

            break

    return


if __name__ == "__main__":
    main()
