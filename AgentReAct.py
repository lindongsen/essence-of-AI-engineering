#!/usr/bin/env python
# encoding: utf-8

# this is a ai agent, it running in ReAct framework.
# it can think, act, observe and give final answer.
# it can use tool exec_cmd to execute command line in local system.

import os
from dotenv import load_dotenv
import argparse

from ai_base.agent_base import (
    StepCallBase,
    AgentRun,
)
from utils.print_tool import (
    enable_flag_print_step,
    disable_flag_print_step,
)
from tools.cmd_tool import (
    exec_cmd,
)


# define prompt of ReAct framework
SYSTEM_PROMPT = """
你需要穿插"thought,action,observation,final_answer"这些步骤去解决任务：
1. thought用于推理当前形势，若最终答案可以确定，则进入final_answer步骤，否则进入action步骤；
2. action用于主动向用户发起请求，你会决定出工具，用户会调用工具；
3. observation是来自用户的答复，你需要观察和分析这个答复，并进入thought步骤。
4. final_answer是最终答案，到达这个步骤则问题已经解决。

注意：
- 当你遇到模糊的问题，如，不清楚操作系统版本、命令行工具是否存在等情况，应该进入action步骤去决定出一个工具，从而让用户能够执行，之后你会得到一个来自用户的observation返回。
- 你会对observation的内容进行思考，继续进入thought步骤去推理当前形势，循环往复，直到得到最终答案。
- 当用户没有提出具体问题时，就只有1个thought的回答；否则每次回答必须会有两个内容：1个是thought，1个是action或final_answer。
- 当任务目标会生成新文件时：若目标文件已经存在，不可修改目标文件，包括：重命名、删除、覆盖等；如果目标文件已存在，你需要验证文件正确性，若正确则代表该文件可用，若不正确则任务失败，之后都会进入final_answer步骤。

输出格式要求：
1. 所有步骤必须严格使用(JSON)格式输出，当有超过1个输出时使用(list)格式将(json)作为元素按照顺序输出;
```
(JSON)支持的(关键字)如下。
- step_name, 步骤名称，字符串格式
- raw_text, 原始内容，字符串格式
- tool_call, 指定工具名，字符串格式，仅action步骤使用
- tool_args, 指定工具参数，JSON格式，仅action步骤使用
```
2. 当用户(要求)或(想要)输出其它格式，你只能输出到(raw_text)这个关键字中，(不能)改变所有步骤的输出格式。
3. 所有步骤不能使用代码块格式去输出，包括但不限于：(```)，(```json)等。

输出示例：
```
[
  {
    "step_name": "thought",
    "raw_text": "我需要知道当前操作系统的版本信息，以便确定后续的操作步骤。"
  },
  {
    "step_name": "action",
    "tool_call": "cmd_tool.exec_cmd",
    "tool_args": {"cmd_string": "uname -a" },
    "raw_text": "我将使用exec_cmd工具来获取操作系统的版本信息。"
  }
]
```
"""

# define global variables
g_flag_interactive = True


class Step4ReAct(StepCallBase):
    """ running on ReAct mode """
    def _execute(self, step:dict, tools:dict, response:list, index:int):
        """ acting steps """
        step_name = step["step_name"]
        if step_name == 'action':
            tool = step['tool_call']
            args = step['tool_args']
            tool_func = tools.get(tool)
            if tool_func is not None:
                obs = tool_func(**args)
                obs_json = {
                    "step_name": "observation",
                    "raw_text": obs
                }
                self.tool_msg = obs_json
                self.code = self.CODE_STEP_FINAL
                return
            else:
                self.result = (f"unknown tool {tool}, exiting.")
                self.code = self.CODE_TASK_FAILED
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

def get_agent(user_prompt=""):
    return AgentRun(
        SYSTEM_PROMPT + "\n" + user_prompt,
        tools=None,
        agent_name="AgentReAct",
    )

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


def main():
    """ return nothing """
    load_dotenv()  # load environment variables from .env file if present

    params = get_params()

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
