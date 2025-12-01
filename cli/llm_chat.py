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

import sys
import os
from dotenv import load_dotenv

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from logger import logger
from ai_base.llm_base import LLMModel, ContentStdout
from ai_base.prompt_base import PromptBase
from utils import env_tool
from utils.thread_local_tool import set_thread_var, KEY_SESSION_ID

from context.ctx_manager import get_session_manager
from context.session_manager.__base import SessionData

def get_message():
    """ return str for message """
    message = ' '.join(sys.argv[1:])

    # message from file
    file_path = message
    if sys.argv[1] == '-':
        file_path = "/dev/stdin"
    if file_path and os.path.exists(file_path):
        with open(file_path) as fd:
            message = fd.read()

    message = message.strip()
    assert message, "message is null"
    return message

def main():
    """ main entry """
    load_dotenv()

    message = get_message()

    # session
    session_id = os.getenv("SESSION_ID")
    messages_from_session = None
    if session_id:
        print(f"session_id: {session_id}")
        set_thread_var(KEY_SESSION_ID, session_id)
        session_mgr = get_session_manager()
        if session_mgr.exists_session(session_id):
            messages_from_session = session_mgr.retrieve_messages(session_id)
            logger.info(f"retrieve messages: session_id={session_id}, count={len(messages_from_session)}")
        else:
            session_mgr.create_session(
                SessionData(session_id=session_id, task=message)
            )

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

    llm_model = LLMModel()
    llm_model.content_senders.append(ContentStdout())
    llm_model.max_tokens = max(1600, llm_model.max_tokens)
    llm_model.temperature = 0.97

    prompt_ctl = PromptBase(sys_prompt_content or "You are a helpful assistant.")
    if messages_from_session:
        prompt_ctl.messages = messages_from_session
        prompt_ctl.add_user_message(message)
    else:
        prompt_ctl.new_session(message)

    if not env_tool.is_debug_mode():
        print(f">>> message:\n{message}")
        print(">>> answer:")
    answer = llm_model.chat(prompt_ctl.messages, for_raw=True, for_stream=True)
    prompt_ctl.add_assistant_message(answer)
    print()

if __name__ == "__main__":
    main()
