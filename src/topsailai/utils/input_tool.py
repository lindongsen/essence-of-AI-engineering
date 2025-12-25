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

from . import env_tool

SPLIT_LINE = "--------------------------------------------------------------------------------"
INPUT_TIPS = ">>> Your Turn: "


def input_one_line(tips=""):
    if not tips:
        tips = INPUT_TIPS

    message = ""
    while True:
        message = input(tips)
        message = message.strip()
        if not message:
            continue
        if message in ["exit", "quit"]:
            sys.exit(0)
        break
    return message

def input_multi_line(tips=""):
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
            if message.strip() in ["exit", "quit"]:
                sys.exit(0)

    message = message.strip()
    if message:
        if message in ["exit", "quit", "/exit", "/quit"]:
            sys.exit(0)
        return message
    return input_multi_line(tips)

def input_message(tips=""):
    """ enter message """
    print(SPLIT_LINE)
    if env_tool.is_chat_multi_line():
        return input_multi_line(tips)
    return input_one_line(tips)

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
    if not message:
        message = input_message()
    return message
