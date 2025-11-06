import os
import sys
import time
import simplejson
import openai

from logger.log_chat import logger
from utils.print_tool import (
    print_error,
)
from utils.json_tool import to_json_str
from utils import env_tool
from context.token import TokenStat


class JsonError(Exception):
    """ invalid json string """
    pass


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

    for count in range(3):
        try:
            response = to_json_str(response)
            return _to_list(simplejson.loads(response))
        except Exception as e:
            print_error(f"parsing response: {e}\n>>>\n{response}\n<<<\nretrying times: {count}")

    raise JsonError("invalid json string")


class ContentSender(object):
    """ send content to endpoint. """
    def send(self, content):
        """ send content to endpoint """
        raise NotImplementedError

class ContentStdout(ContentSender):
    """ send content to stdout """
    def send(self, content):
        """ write content to stdout """
        sys.stdout.write(content)


class LLMModel(object):
    def __init__(self, max_tokens=80000):
        self.max_tokens = int(os.getenv("MAX_TOKENS", max_tokens))
        self.openai_model_name = os.getenv("OPENAI_MODEL", "DeepSeek-V3.1-Terminus")
        self.model = self.get_llm_model()

        logger.info(f"model={self.openai_model_name}, max_tokens={max_tokens}")

        self.tokenStat = TokenStat(id(self))

        self.content_senders = [] # instances of base class ContentSender

    def send_content(self, content):
        for sender in self.content_senders:
            sender.send(content)
        return

    def __del__(self):
        self.tokenStat.flag_running = False

    # get a object abount llm model by openai api
    def get_llm_model(self):
        return openai.OpenAI(
            api_key=os.getenv("OPENAI_API_KEY", ""),
            base_url=os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1"),
        ).chat.completions

    def call_llm_model(self, messages):
        self.tokenStat.add_msgs(messages)

        response = self.model.create(
            model=self.openai_model_name,
            messages=messages,
            temperature=0,
            max_tokens=self.max_tokens,
            n=1,
            stop=None,
        )

        self.tokenStat.output_token_stat()

        full_content = response.choices[0].message.content.strip()
        self.send_content(full_content)

        return full_content

    def call_llm_model_by_stream(self, messages):
        self.tokenStat.add_msgs(messages)

        response = self.model.create(
            model=self.openai_model_name,
            messages=messages,
            temperature=0,
            max_tokens=self.max_tokens,
            n=1,
            stop=None,
            stream=True,
        )

        full_content = ""
        for chunk in response:
            delta_content = chunk.choices[0].delta.content
            if delta_content:
                full_content += delta_content
                self.send_content(delta_content)

        if env_tool.is_debug_mode():
            print()

        self.tokenStat.output_token_stat()

        return full_content.strip()

    def chat(self, messages, for_raw=False, for_stream=False):
        """ return list_dict """
        retry_times = 10
        for i in range(100):
            if i > retry_times:
                break

            if i > 0:
                sec = (i%retry_times)*5
                if sec <= 0:
                    sec = 3
                print_error(f"[{i}] blocking chat {sec}s ...")
                time.sleep(sec)

            try:
                if for_stream:
                    rsp = self.call_llm_model_by_stream(messages)
                else:
                    rsp = self.call_llm_model(messages)
                if for_raw:
                    return rsp
                return _format_response(rsp)
            except JsonError as e:
                print_error(f"!!! [{i}] JsonError, {e}")
                continue
            except openai.RateLimitError as e:
                print_error(f"!!! [{i}] RateLimitError, {e}")
                if i > 7:
                    retry_times += 1
                continue
            except TypeError as e:
                print_error(f"!!! [{i}] TypeError, {e}")
                continue
            except openai.InternalServerError as e:
                print_error(f"!!! [{i}] InternalServerError, {e}")
                if i > 7:
                    retry_times += 1
                continue
            except openai.APIConnectionError as e:
                print_error(f"!!! [{i}] APIConnectionError, {e}")
                if i > 7:
                    retry_times += 1
                continue
            except openai.APITimeoutError as e:
                print_error(f"!!! [{i}] APITimeoutError, {e}")
                if i > 7:
                    retry_times += 1
                continue

        raise Exception("chat to LLM is failed")
