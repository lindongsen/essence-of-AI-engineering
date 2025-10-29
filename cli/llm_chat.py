#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
  Author: DawsonLin
  Email: lin_dongsen@126.com
  Created: 2025-10-19
  Purpose:
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

    llm_model = LLMModel()
    llm_model.content_senders.append(ContentStdout())

    prompt_ctl = PromptBase("You are a helpful assistant.")
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
