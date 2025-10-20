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

from ai_base.llm_base import LLMModel
from ai_base.prompt_base import PromptBase


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
    llm_model = LLMModel()

    prompt_ctl = PromptBase("You are a helpful assistant.")
    prompt_ctl.new_session(message)

    print(f">>> message:\n{message}")
    answer = llm_model.chat(prompt_ctl.messages, for_raw=True)
    prompt_ctl.add_assistant_message(answer)
    print(f">>> answer:\n{answer}")

if __name__ == "__main__":
    main()
