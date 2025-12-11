from topsailai.logger.log_chat import logger
from topsailai.utils.print_tool import (
    print_error,
)

from topsailai.ai_base.prompt_base import (
    PromptBase,
)
from topsailai.ai_base.llm_base import (
    LLMModel,
)
from topsailai.utils.thread_local_tool import (
    ctxm_give_agent_name,
    ctxm_set_agent,
)
from topsailai.tools import get_tool_prompt, TOOLS as INTERNAL_TOOLS


class StepCallBase(object):
    """ the datastructure of return value of step_call(...) """
    CODE_TASK_FINAL = 0
    CODE_STEP_FINAL = 1
    CODE_TASK_FAILED = -1

    def __init__(self, flag_interactive:bool=False):

        # for result
        self.code = None
        self.user_msg = None
        self.tool_msg = None
        self.result = None

        # flags
        self.flag_interactive = True if flag_interactive else False

        return

    def __call__(self, *args, **kwds):
        # it must init all of result for each call
        self.__init__()
        self._execute(*args, **kwds)
        return self

    def _execute(self, step:dict, tools:dict, response:list, index:int):
        """ override this method """
        raise NotImplementedError("Subclasses must implement this method")

class AgentBase(PromptBase):
    """ AI-Agent base class """
    def __init__(
            self,
            system_prompt:str,
            tools:dict,
            agent_name:str,
            tool_prompt:str="",
            tool_kits:list=None,
            excluded_tool_kits:list=None,
        ):
        """
        :tools: dict, the specific tools, key is tool_name, value is function;
        :tool_kits: list, the internal tools list, [name1, name2];
        """
        self.system_prompt = system_prompt
        self.tools = tools
        self.agent_name = agent_name
        assert self.system_prompt, "system_prompt is required"

        if self.tools:
            if not tool_prompt:
                tool_prompt = get_tool_prompt(None, self.tools)

        self.llm_model = LLMModel()

        if not self.tools and not tool_kits:
            # using all of internal tools.
            tool_kits = list(INTERNAL_TOOLS.keys())

        if tool_kits and excluded_tool_kits:
            for tool_name in excluded_tool_kits:
                if tool_name in tool_kits:
                    tool_kits.remove(tool_name)
                    continue
                for _tool in tool_kits[:]:
                    if _tool.startswith(tool_name):
                        if _tool in tool_kits:
                            tool_kits.remove(_tool)

        super(AgentBase, self).__init__(self.system_prompt, tool_prompt, tool_kits)
        return

    @property
    def max_tokens(self) -> int:
        """ get max tokens """
        return self.llm_model.max_tokens

    @property
    def all_tools(self):
        """ return all of available tools. include of internal tools. """
        all_tools = {}
        # first, internal tools
        all_tools.update(INTERNAL_TOOLS)

        # second, specific tools for this agent.
        if self.tools:
            all_tools.update(self.tools)

        return all_tools

    def run(self, step_call:StepCallBase, user_input:str):
        """ run this agent """
        with (
                ctxm_give_agent_name(self.agent_name),
                ctxm_set_agent(self),
            ):
            try:
                return self._run(step_call, user_input)
            finally:
                if self.flag_dump_messages:
                    self.dump_messages()

    def _run(self, step_call:StepCallBase, user_input:str):
        raise NotImplementedError("Subclasses must implement this method")

class AgentRun(AgentBase):
    """ a common of running steps """
    def _run(self, step_call:StepCallBase, user_input:str):
        """ return final answer, or None if error """
        if user_input:
            self.new_session({"step_name":"task","raw_text":user_input})

        all_tools = self.all_tools

        while True:
            response = self.llm_model.chat(self.messages)
            if not response:
                print_error("No response from LLM.")
                return None
            self.add_assistant_message(response)

            ctx_count = len(self.messages)

            for i, step in enumerate(response):
                ret = step_call(step, tools=all_tools, response=response, index=i)
                assert isinstance(ret, StepCallBase), "step_call must return StepCallBase instance"
                if ret.code == ret.CODE_TASK_FINAL:
                    logger.info(f"final: {ret.result}")
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

            # update env
            self.update_message_for_env()

        # raise RuntimeError("Unreachable code reached")
