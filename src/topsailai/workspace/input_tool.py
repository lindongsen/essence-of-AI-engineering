'''
  Author: DawsonLin
  Email: lin_dongsen@126.com
  Created: 2025-12-19
  Purpose:
'''

import os
import sys

# DONOT DELETE THIS FOR FUNCTION 'input'
import readline

from topsailai.utils import env_tool
from topsailai.workspace.hook_instruction import HookInstruction

SPLIT_LINE = "--------------------------------------------------------------------------------"
INPUT_TIPS = ">>> Your Turn: "

DESCRIPTION_EXIT_SET = ["exit", "quit", "/exit", "/quit"]

def hook_message(message:str, hook:HookInstruction) -> bool:
    """ if has call hook, return True. """
    message = message.strip()
    if not message:
        return False

    if message in DESCRIPTION_EXIT_SET:
        sys.exit(0)

    if hook is None:
        return False

    if hook.exist_hook(message):
        hook.call_hook(message)
        return True
    return False

def input_one_line(tips="", hook:HookInstruction=None):
    if not tips:
        tips = INPUT_TIPS

    message = ""
    while True:
        message = input(tips)
        message = message.strip()
        if not message:
            continue
        if hook_message(message, hook):
            continue
        break
    return message

def input_multi_line(tips="", hook:HookInstruction=None):
    if not tips:
        tips = INPUT_TIPS

    print(tips + " Press 'CTRL D' or Enter 'EOF' for end")
    message = ""
    count = 0
    while True:
        count += 1

        try:
            line = input()
            if line == "EOF":
                break
            message += line + "\n"
        except EOFError:
            break

        if count == 1:
            if hook_message(message, hook):
                message = ""
                break

    message = message.strip()
    if message:
        if not hook_message(message, hook):
            return message
    return input_multi_line(tips, hook)

def input_message(tips="", hook:HookInstruction=None):
    """ enter message """
    print(SPLIT_LINE)
    if env_tool.is_chat_multi_line():
        return input_multi_line(tips, hook)
    return input_one_line(tips, hook)

def get_message(hook:HookInstruction=None):
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
    if not message:
        message = input_message(hook=hook)
    return message

def input_yes(tips="Continue [yes/no] ") -> bool:
    yn = input(tips)
    return yn.strip().lower() == "yes"
