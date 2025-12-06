#!/usr/bin/env python

# this is a ai agent, it running in Plan-And-Execute framework.
# it can plan a task into multiple sub-tasks, and execute them one by one.
# it can use tool agent_shell to execute single sub-task.

import os
import sys
import argparse
from dotenv import load_dotenv

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
    sys.path.insert(0, project_root + "/src")

os.chdir(project_root)

#from logger import logger
from ai_base.agent_base import (
    AgentRun,
)
from ai_base.agent_types.plan_and_execute import (
    SYSTEM_PROMPT,
    StepCall4PlanAndExecute,
)

from tools import agent_tool


def agent_shell(message):
    """
    # parameters
    :message: string

    # return
    json like {"step_name":"subtask_result","raw_text":"ok"}
    """
    final_answer = agent_tool.agent_programmer(message)
    return {"step_name":"subtask_result","raw_text":final_answer}

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
    args = parser.parse_args()
    params = {
        "prompt_file": args.prompt_file,
        "prompt_content": "",
        "task": args.task
    }

    # get prompt content
    if params["prompt_file"]:
        with open(params["prompt_file"], "r") as fd:
            params["prompt_content"] = fd.read() or ""

    return params

def get_agent(user_prompt=""):
    return AgentRun(
        SYSTEM_PROMPT + "\n====\n" + user_prompt,
        tools={"agent_shell": agent_shell},
        agent_name="AgentPlanAndExecute",
        excluded_tool_kits=agent_tool.get_all_agent_tools().keys()
    )

def run_once(user_input, user_prompt=""):
    """ return final answer, or None if error """
    assert user_input, "missing user_input"
    agent = get_agent(user_prompt)
    return agent.run(StepCall4PlanAndExecute(), user_input)

def main():
    """ return nothing """
    load_dotenv()  # load environment variables from .env file if present

    params = get_params()

    # run once mode
    if params["task"]:
        final_answer = run_once(params["task"], params["prompt_content"])
        if final_answer:
            print(f"\n>>> Final Answer: {final_answer}")
        else:
            print("Failed to get a final answer.")
        return

    # interactive mode
    print("Welcome to the Plan-And-Execute AI Agent. Type 'exit' to quit.")
    while True:
        user_input = input("\n>>> Enter your task: ")
        if user_input.lower() in ['exit', 'quit']:
            print("Exiting. Goodbye!")
            break
        if not user_input.strip():
            continue
        final_answer = run_once(user_input, params["prompt_content"])
        if final_answer:
            print(f"\n>>> Final Answer: {final_answer}")
        else:
            print("Failed to get a final answer.")
    return

if __name__ == "__main__":
    main()
