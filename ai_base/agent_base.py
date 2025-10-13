from utils.print_tool import (
    print_step,
    print_error,
)

from ai_base.llm_base import (
    LLMModel,
    ROLE_USER, ROLE_ASSISTANT, ROLE_SYSTEM, ROLE_TOOL,
    _format_content,
)
from utils.thread_local_tool import ctxm_give_agent_name


class StepCallBase(object):
    """ the datastructure of return value of step_call(...) """
    CODE_TASK_FINAL = 0
    CODE_STEP_FINAL = 1
    CODE_TASK_FAILED = -1

    def __init__(self):

        # for result
        self.code = None
        self.user_msg = None
        self.tool_msg = None
        self.result = None

        return

    def __call__(self, *args, **kwds):
        # it must init all of result for each call
        self.__init__()
        self._execute(*args, **kwds)
        return self

    def _execute(self, step:dict, tools:dict, response:list, index:int):
        """ override this method """
        raise NotImplementedError("Subclasses must implement this method")

class AgentBase(object):
    def __init__(self, system_prompt:str, tools:dict, agent_name:str):
        self.system_prompt = system_prompt
        self.tools = tools
        self.agent_name = agent_name
        assert self.system_prompt, "system_prompt is required"
        assert isinstance(self.tools, dict) and self.tools, "tools must be a non-empty dictionary"

        self.llm_model = LLMModel()
        self.messages = []
        self.reset_messages()

    def reset_messages(self):
        self.messages = []
        self.messages.append({"role": ROLE_SYSTEM, "content": self.system_prompt})

    def add_user_message(self, content):
        if content is None:
            return
        content = _format_content(content)
        print_step(content)
        self.messages.append({"role": ROLE_USER, "content": content})

    def add_assistant_message(self, content):
        if content is None:
            return
        content = _format_content(content)
        print_step(content)
        self.messages.append({"role": ROLE_ASSISTANT, "content": content})

    def add_tool_message(self, content):
        if content is None:
            return
        content = _format_content(content)
        print_step(content)
        self.messages.append({"role": ROLE_TOOL, "content": content})

    def run(self, step_call:StepCallBase, user_input:str):
        with ctxm_give_agent_name(self.agent_name):
            return self._run(step_call, user_input)

    def _run(self, step_call:StepCallBase, user_input:str):
        raise NotImplementedError("Subclasses must implement this method")

class AgentRun(AgentBase):
    def _run(self, step_call:StepCallBase, user_input:str):
        """ return final answer, or None if error """
        self.reset_messages()
        self.add_user_message({"step_name":"task","raw_text":user_input})

        while True:
            response = self.llm_model.chat(self.messages)
            if not response:
                print_error("No response from LLM.")
                return None
            self.add_assistant_message(response)

            ctx_count = len(self.messages)

            for i, step in enumerate(response):
                ret = step_call(step, tools=self.tools, response=response, index=i)
                assert isinstance(ret, StepCallBase), "step_call must return StepCallBase instance"
                if ret.code == ret.CODE_TASK_FINAL:
                    return ret.result
                elif ret.code == ret.CODE_TASK_FAILED:
                    print_error(f"Task failed: {ret.result}")
                    return None
                elif ret.code == ret.CODE_STEP_FINAL:
                    self.add_user_message(ret.user_msg)
                    self.add_tool_message(ret.tool_msg)
                    break

            # end for step in response

            if len(self.messages) == ctx_count:
                print_error("No progress made in this iteration, exiting.")
                return None
        # raise RuntimeError("Unreachable code reached")
