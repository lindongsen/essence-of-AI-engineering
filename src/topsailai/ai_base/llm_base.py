import os
import sys
import time
import random
import simplejson
import openai
from openai.types.chat import ChatCompletionMessage

from topsailai.logger.log_chat import logger
from topsailai.utils.print_tool import (
    print_error,
    print_debug,
)
from topsailai.utils.json_tool import to_json_str
from topsailai.utils import (
    env_tool,
    format_tool,
)
from topsailai.context.token import TokenStat


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

def _format_messages(messages, key_name, value_name):
    """ format messages to specific format """
    func_format = None # func(content, key_name, value_name)

    if format_tool.TOPSAILAI_FORMAT_PREFIX in messages[0]["content"]:
        func_format = format_tool.to_topsailai_format

    if func_format is None:
        return messages

    for msg in messages[2:]:
        if msg["content"][0] in ["[", "{"]:
            new_content = func_format(
                msg["content"],
                key_name=key_name,
                value_name=value_name,
            )
            if new_content:
                msg["content"] = new_content.strip()

    #logger.info(simplejson.dumps(messages, indent=2, default=str))

    return messages

def _format_response(response):
    """ format response to list if it is json string """
    if isinstance(response, (list, dict)):
        return _to_list(response)

    if isinstance(response, str):
        response = response.strip()
        if not response:
            raise JsonError("null of response")

    for count in range(3):
        try:
            if response.startswith(format_tool.TOPSAILAI_FORMAT_PREFIX) or \
                f"\n{format_tool.TOPSAILAI_FORMAT_PREFIX}" in response:
                    if count:
                        # no need retry
                        break
                    return format_tool.format_dict_to_list(
                        format_tool.parse_topsailai_format(response),
                        key_name="step_name",
                        value_name="raw_text",
                    )

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


def parse_model_settings():
    """Parse model settings from the MODEL_SETTINGS environment variable.

    The variable should contain settings in the format: key1=value1,key2=value2;key3=value3,key4=value4

    Items are separated by ';', and within each item, key-value pairs are separated by ','.

    Each key-value pair is separated by '='.

    Returns a list of dictionaries, where each dictionary represents one item.

    Example:

        MODEL_SETTINGS="k1_a=v1_a,k2_a=v2_a;k1_b=v1_b,k2_b=v2_b"

        Returns: [{"k1_a": "v1_a", "k2_a": "v2_a"}, {"k1_b": "v1_b", "k2_b": "v2_b"}]

    """
    settings_str = os.getenv("MODEL_SETTINGS")
    if not settings_str:
        return []
    items = settings_str.split(';')
    result = []
    for item in items:
        item = item.strip()
        if not item:
            continue
        kv_pairs = item.split(',')
        d = {}
        for kv in kv_pairs:
            kv = kv.strip()
            if '=' in kv:
                k, v = kv.split('=', 1)
                d[k.strip()] = v.strip()
        if d:  # only append if dict is not empty
            result.append(d)
    return result


class LLMModel(object):
    def __init__(
            self,
            max_tokens=8000,
            temperature=0.3,
            top_p=0.97,
            frequency_penalty=0.0,
            model_name=None,
        ):
        self.max_tokens = int(os.getenv("MAX_TOKENS", max_tokens))
        self.temperature = float(os.getenv("TEMPERATURE", temperature))
        self.top_p = float(os.getenv("TOP_P", top_p))
        self.frequency_penalty = float(os.getenv("FREQUENCY_PENALTY", frequency_penalty))

        self.model_name = model_name or os.getenv("OPENAI_MODEL", "DeepSeek-V3.1-Terminus")
        self.model_config = {"api_key": "", "api_base": ""} # in using
        self.model = self.get_llm_model() # in using

        # multiple models, list_dict, _model=self.get_llm_model(model_config)
        self.models = [] # supported
        self.get_llm_models()

        logger.info(f"model={self.model_name}, max_tokens={max_tokens}")

        self.tokenStat = TokenStat(id(self))

        self.content_senders = [] # instances of base class ContentSender

    def send_content(self, content):
        for sender in self.content_senders:
            sender.send(content)
        return

    def __del__(self):
        self.tokenStat.flag_running = False

    @property
    def chat_model(self):
        """ get a available model object to chat """
        if self.models:
            self.model_config = random.choice(self.models)
            self.model = self.model_config["_model"]
        return self.model

    def get_llm_models(self):
        """ add model to self.models;

        self.models format is list_dict;

        About dict:
            :api_key: a secret key
            :api_base: a url link
            :_model: the object of chat

        return self.models.
        """
        model_settings = parse_model_settings()
        if not model_settings:
            return
        for model_config in model_settings:
            _model = self.get_llm_model(
                api_key=model_config["api_key"],
                api_base=model_config.get("api_base"),
            )
            model_config["_model"] = _model
            self.models.append(model_config)
        return self.models

    # get a object abount llm model by openai api
    def get_llm_model(self, api_key=None, api_base=None):
        logger.info("getting llm model ...")
        return openai.OpenAI(
            api_key=api_key or os.getenv("OPENAI_API_KEY", ""),
            base_url=api_base or os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1"),
        ).chat.completions

    def build_parameters_for_chat(self, messages, stream=False, tools=None, tool_choice="auto"):
        _format_messages(messages, key_name="step_name", value_name="raw_text")
        params = dict(
            model=self.model_name,
            messages=messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            top_p=self.top_p,
            frequency_penalty=self.frequency_penalty,
            n=1,
            stop=None,
            stream=stream,
        )

        if tools:
            params["tools"] = tools
            params["tool_choice"] = tool_choice

        return params

    def debug_response(self, response, content):
        """ debug mode """
        if not env_tool.is_debug_mode():
            return

        if content is None:
            return
        if response is None:
            return

        content = content.strip()

        def _need_print() -> bool:
            if not content:
                return True
            #if 'tool_call' in content:
            #    return True
            #if '"action"' in content and '"tool_call":' not in content:
            #    return True
            return False

        if _need_print():
            print_debug("[RESPONSE] \n" + simplejson.dumps(response.__dict__, indent=2, ensure_ascii=False, default=str))

        return

    def get_response_message(self, response) -> ChatCompletionMessage:
        """
        ChatCompletionMessage(
            content='',
            refusal=None,
            role='assistant',
            annotations=None,
            audio=None,
            function_call=None,
            tool_calls=None),
            refs=None,
            service_tier=None
        )
        """
        return response.choices[0].message

    def call_llm_model(self, messages, tools=None, tool_choice="auto"):
        """ return tuple (response:obj, content:str) """
        self.tokenStat.add_msgs(messages)

        response = self.chat_model.create(
            **self.build_parameters_for_chat(
                messages,
                tools=tools, tool_choice=tool_choice,
            )
        )

        self.tokenStat.output_token_stat()

        full_content = response.choices[0].message.content
        try:
            self.debug_response(response, full_content)
        except Exception as e:
            print_error(f"[DEBUG] {e}")

        if full_content is None:
            raise TypeError("no response")
        full_content = full_content.strip()
        if not full_content:
            raise TypeError("null of response")

        self.send_content(full_content)

        return (response, full_content)

    def call_llm_model_by_stream(self, messages):
        """ return tuple (response:obj, content:str) """
        self.tokenStat.add_msgs(messages)

        response = self.chat_model.create(
            **self.build_parameters_for_chat(messages, stream=True)
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

        return (response, full_content.strip())

    def chat(
            self, messages,
            for_raw=False,
            for_stream=False,
            for_response=False,
            tools=None,
            tool_choice="auto",
        ):
        """
        Args:
            for_response: if True, return (response:obj, content:list[dict])

        default return list_dict.
        """
        retry_times = 10
        err_count_map = {}

        rsp_content = None
        rsp_obj = None

        for i in range(100):
            if i > retry_times:
                break

            if i > 0:
                sec = (i%retry_times)*5
                if sec <= 0:
                    sec = 3
                if sec > 120:
                    sec = 120
                print_error(f"[{i}] blocking chat {sec}s ...")
                time.sleep(sec)

            try:
                if for_stream:
                    rsp_obj, rsp_content = self.call_llm_model_by_stream(messages)
                else:
                    rsp_obj, rsp_content = self.call_llm_model(
                        messages,
                        tools=tools, tool_choice=tool_choice,
                    )

                if for_raw:
                    return rsp_content

                result = _format_response(rsp_content)

                if for_response:
                    return (rsp_obj, result)

                return result
            except JsonError as e:
                print_error(f"!!! [{i}] JsonError, {e}")
                continue
            except openai.RateLimitError as e:
                print_error(f"!!! [{i}] RateLimitError, {self.model_config["api_key"][:7]}, {e}")
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

                if 'InternalServerError' not in err_count_map:
                    err_count_map["InternalServerError"] = 0
                err_count_map["InternalServerError"] += 1

                if err_count_map["InternalServerError"] > 5:
                    self.model = self.get_llm_model()

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
            except openai.PermissionDeniedError as e:
                print_error(f"!!! [{i}] PermissionDeniedError, {e}")
                continue
            except openai.BadRequestError as e:
                # I don't know why some large model services return this issue, but retrying usually resolves it.
                print_error(f"!!! [{i}] BadRequestError, {e}")

                # case: Requested token count exceeds the model's maximum context length
                e_str = str(e).lower()
                for key in [
                    "exceed",
                    "maximum context",
                ]:
                    if key in e_str:
                        break

                continue

        raise Exception("chat to LLM is failed")
