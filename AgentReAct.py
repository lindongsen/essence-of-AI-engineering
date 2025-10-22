#!/usr/bin/env python
# encoding: utf-8

# this is a ai agent, it running in ReAct framework.
# it can think, act, observe and give final answer.
# it can use tool exec_cmd to execute command line in local system.

import os
import argparse
from dotenv import load_dotenv

from prompt_hub.prompt_tool import PromptHubExtractor
from ai_base.agent_base import (
    StepCallBase,
    AgentRun,
)
from ai_base.prompt_base import PromptBase
from utils.print_tool import (
    enable_flag_print_step,
    disable_flag_print_step,
)


# define prompt of ReAct framework
SYSTEM_PROMPT = PromptHubExtractor.prompt_mode_ReAct

# define global variables
g_flag_interactive = True


class Step4ReAct(StepCallBase):
    """ running on ReAct mode """
    def _execute(self, step:dict, tools:dict, response:list, index:int):
        """ acting steps """
        step_name = step["step_name"]
        if step_name == 'action':

            if 'tool_call' not in step:
                # LLM mistake, missing argv
                obs_json = {
                    "step_name": "observation",
                    "raw_text": "missing tool_call"
                }
                self.tool_msg = obs_json
                self.code = self.CODE_STEP_FINAL
                return

            tool = step['tool_call']
            args = step.get('tool_args') or {}
            tool_func = tools.get(tool)

            if tool_func is not None:
                try:
                    obs = tool_func(**args)
                except Exception as e:
                    obs = str(e)
                obs_json = {
                    "step_name": "observation",
                    "raw_text": obs
                }
                self.tool_msg = obs_json
                self.code = self.CODE_STEP_FINAL
                return
            else:
                # LLM mistake, no found this tool
                obs_json = {
                    "step_name": "observation",
                    "raw_text": f"no found such as tool: {tool}"
                }
                self.tool_msg = obs_json
                self.code = self.CODE_STEP_FINAL
                return
        elif step_name == "thought":
            if len(response) == 1:
                if not g_flag_interactive:
                    self.code = self.CODE_TASK_FAILED
                    self.result = ("only thought step without action or final_answer in non-interactive mode, exiting.")
                    return
                # interactive mode, ask user for more input
                # only thought, no action or final_answer, ask user for more input
                user_input = input("\n>>> Your input: ")
                self.user_msg = user_input
                self.code = self.CODE_STEP_FINAL
                return
        elif step_name == 'final_answer':
            self.result = step["raw_text"]
            self.code = self.CODE_TASK_FINAL
            return

        return

def get_agent(user_prompt="", to_dump_messages=False):
    """ return a agent object. """
    agent = AgentRun(
        SYSTEM_PROMPT + "\n====\n" + user_prompt,
        tools=None,
        agent_name="AgentReAct",
    )

    # set flags
    if to_dump_messages:
        agent.flag_dump_messages = True

    return agent

def run_once(user_input, to_print_step=None, user_prompt=""):
    """ return final answer, or None if error """
    assert user_input, "user_input is required"
    if to_print_step:
        enable_flag_print_step()
    elif to_print_step is False:
        disable_flag_print_step()

    global g_flag_interactive
    g_flag_interactive = False
    if os.getenv("INTERACTIVE") == "1":
        g_flag_interactive = True

    agent = get_agent(user_prompt)
    final_answer = agent.run(Step4ReAct(), user_input)
    return final_answer

def continue_task(msg_file):
    """ continue a task """
    agent = get_agent()
    agent.load_messages(msg_file)
    final_answer = agent.run(Step4ReAct(), "")
    return final_answer

def get_params():
    ''' return dict for parameters '''
    parser = argparse.ArgumentParser(
        usage="",
        description=""
    )
    parser.add_argument(
        "-p", "--prompt_file", required=False, dest="prompt_file", type=str,
        default=None,
        help="give a prompt file to extend system prompt"
    )
    parser.add_argument(
        "-t", "--task", required=False, dest="task", type=str,
        default=None,
        help="give a task for runonce mode"
    )
    parser.add_argument(
        "--dump_msg", action="store_true", required=False, dest="flag_dump_messages",
        default=False,
        help="dump all of messages to a file"
    )
    parser.add_argument(
        "--msg_file", required=False, dest="msg_file", type=str,
        default=None,
        help="use the msg_file to continue a task"
    )
    args = parser.parse_args()
    params = {
        "prompt_file": args.prompt_file,
        "prompt_content": "",
        "task": args.task,
        "flag_dump_messages": args.flag_dump_messages,
        "msg_file": args.msg_file,
    }

    # get prompt content
    if params["prompt_file"]:
        with open(params["prompt_file"], "r") as fd:
            params["prompt_content"] = fd.read() or ""

    # set flags
    if params["flag_dump_messages"]:
        PromptBase.flag_dump_messages = True

    return params


def main():
    """ return nothing """
    load_dotenv()  # load environment variables from .env file if present

    params = get_params()

    # continue a task
    if params["msg_file"]:
        final_answer = continue_task(params["msg_file"])
        if final_answer:
            print(f"\n>>> Final Answer:\n{final_answer}")
        else:
            print("Failed to get a final answer.")
        return

    # run once mode
    if params["task"]:
        final_answer = run_once(
            user_input=params["task"],
            user_prompt=params["prompt_content"]
        )
        if final_answer:
            print(f"\n>>> Final Answer:\n{final_answer}")
        else:
            print("Failed to get a final answer.")
        return

    # interactive mode
    agent = get_agent(params["prompt_content"])
    print("Welcome to the AI Agent Shell. Type 'exit' to quit.")
    while True:
        user_input = input("\n>>> Enter your task: ")
        if user_input.lower() in ['exit', 'quit']:
            break
        if user_input.strip() == "":
            continue
        final_answer = agent.run(Step4ReAct(), user_input)
        if final_answer:
            print(f"\nFinal Answer: {final_answer}")
        else:
            print("Failed to get a final answer.")
    return

if __name__ == "__main__":
    main()
