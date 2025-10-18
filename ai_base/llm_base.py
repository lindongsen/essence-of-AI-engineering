import os
import simplejson
import openai

from utils.print_tool import (
    print_error,
)
from utils.json_tool import to_json_str

# define roles
ROLE_USER = "user"
ROLE_ASSISTANT = "assistant"
ROLE_SYSTEM = "system"
ROLE_TOOL = "tool"

def _to_list(obj):
    """ convert obj to list if it is not list """
    if isinstance(obj, list):
        return obj
    if obj is None:
        return None
    if isinstance(obj, (set, tuple)):
        return list(obj)
    return [obj]

def _format_content(content):
    """ format content to json string if it is list/dict """
    return to_json_str(content)

def _format_response(response):
    """ format response to list if it is json string """
    if isinstance(response, (list, dict)):
        return _to_list(response)
    try:
        return _to_list(simplejson.loads(response))
    except Exception as e:
        print_error(f"parsing response: {e}\n>>>\n{response}\n<<<")
    # default to return raw value
    return response


class LLMModel(object):
    def __init__(self, max_tokens=80000):
        self.max_tokens = max_tokens
        self.openai_model_name = os.getenv("OPENAI_MODEL", "DeepSeek-V3.1-Terminus")
        self.model = self.get_llm_model()

    # get a object abount llm model by openai api
    def get_llm_model(self):
        return openai.OpenAI(
            api_key=os.getenv("OPENAI_API_KEY", ""),
            base_url=os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1"),
        ).chat.completions

    def call_llm_model(self, messages):
        response = self.model.create(
            model=self.openai_model_name,
            messages=messages,
            temperature=0,
            max_tokens=self.max_tokens,
            n=1,
            stop=None,
        )
        return response.choices[0].message.content.strip()

    def chat(self, messages):
        """ return list_dict """
        rsp = self.call_llm_model(messages)
        return _format_response(rsp)
