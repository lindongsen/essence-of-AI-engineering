#!/usr/bin/env python

# this is a ai agent, it running in Plan-And-Execute framework.
# it can plan a task into multiple sub-tasks, and execute them one by one.
# it can use tool agent_shell to execute single sub-task.

from dotenv import load_dotenv
import argparse

from prompt_hub import prompt_tool
from ai_base.agent_base import (
    StepCallBase,
    AgentRun,
)

import AgentReAct

# define roles
ROLE_USER = "user"
ROLE_ASSISTANT = "assistant"
ROLE_SYSTEM = "system"
ROLE_TOOL = "tool"

# define prompt of Plan-And-Execute framework
SYSTEM_PROMPT = \
    prompt_tool.read_prompt("work_mode/PlanAndExecute.md") + \
    prompt_tool.read_prompt("security/file.md") + \
    prompt_tool.read_prompt("format/json.md") + \
"""
# Additional notes in JSON
The all of (keywords) supported in (JSON) are as follows:
- step_name, string format
- raw_text, string format
- tool_call, specifies the tool name, string format, used only in the execute-subtask step
- tool_args, specifies tool parameters, JSON format, used only in the execute-subtask step

Output example:
```
[
  {
    "step_name": "thought",
    "raw_text": "hello"
  },
  {
    "step_name": "plan-analysis",
    "raw_text": "world"
  }
]
```

----
"""


def agent_shell(message):
    """
    # parameters
    :message: string

    # return
    json like {"step_name":"subtask_result","raw_text":"ok"}
    """
    final_answer = AgentReAct.run_once(message)
    return {"step_name":"subtask_result","raw_text":final_answer}

class StepCall4PlanAndExecute(StepCallBase):
    """ running on Plan-And-Execute mode """
    def _execute(self, step:dict, tools:dict, response:list, index:int):
        """ acting steps """
        step_name = step.get("step_name", "")
        raw_text = step.get("raw_text", "")
        tool_call = step.get("tool_call", "")
        tool_args = step.get("tool_args", {})

        if step_name == "final":
            self.result = raw_text
            self.code = self.CODE_TASK_FINAL
            return

        elif step_name == "task-ask":
            # Ask user for more information
            user_reply = input(f">>> LLM: {raw_text}\n>>> Your input: ")
            self.user_msg = {"step_name":"task","raw_text":user_reply}
            self.code = self.CODE_STEP_FINAL
            return

        elif step_name == "execute-subtask":
            if tool_call in tools:
                tool_func = tools[tool_call]
                result = tool_func(**tool_args)
                self.tool_msg = result
                self.code = self.CODE_STEP_FINAL
                return
            else:
                self.result = (f"Unknown tool call {tool_call}.")
                self.code = self.CODE_TASK_FAILED
                return

        return

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
