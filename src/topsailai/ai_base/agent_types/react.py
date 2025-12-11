'''
  Author: DawsonLin
  Email: lin_dongsen@126.com
  Created: 2025-12-05
  Purpose:
'''

from topsailai.logger import logger

from topsailai.utils.thread_tool import (
    is_main_thread,
)
from topsailai.prompt_hub.prompt_tool import PromptHubExtractor
from topsailai.ai_base.agent_base import (
    StepCallBase,
)


# define prompt of ReAct framework
SYSTEM_PROMPT = PromptHubExtractor.prompt_mode_ReAct

AGENT_NAME = "AgentReAct"


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
                    logger.exception(e)
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
                if not self.flag_interactive:
                    # for retry
                    self.code = self.CODE_STEP_FINAL
                    self.user_msg = "no found action"
                    # for failed
                    # self.code = self.CODE_TASK_FAILED
                    # self.result = ("only thought step without action or final_answer in non-interactive mode, exiting.")
                    return
                # interactive mode, ask user for more input
                # only thought, no action or final_answer, ask user for more input
                user_input = "continue"
                while True:
                    if not is_main_thread():
                        break
                    user_input = input("\n>>> Your input: ")
                    if not user_input.strip():
                        continue
                    break
                self.user_msg = user_input
                self.code = self.CODE_STEP_FINAL
                return
        elif step_name == 'final_answer':
            self.result = step["raw_text"]
            self.code = self.CODE_TASK_FINAL
            return
        elif len(response) == (index+1):
            # the last element, LLM has a mistake
            logger.error("LLM has a mistake: agent can not handle it [%s]", step_name)
            self.code = self.CODE_STEP_FINAL
            self.user_msg = "I can not handle it"
            return

        return
