import os
import sys
import time
import random
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
        ):
        self.max_tokens = int(os.getenv("MAX_TOKENS", max_tokens))
        self.temperature = float(os.getenv("TEMPERATURE", temperature))
        self.top_p = float(os.getenv("TOP_P", top_p))
        self.frequency_penalty = float(os.getenv("FREQUENCY_PENALTY", frequency_penalty))

        self.openai_model_name = os.getenv("OPENAI_MODEL", "DeepSeek-V3.1-Terminus")

        self.model_name = self.openai_model_name
        self.model_config = {"api_key": "", "api_base": ""} # in using
        self.model = self.get_llm_model() # in using

        # multiple models, list_dict, _model=self.get_llm_model(model_config)
        self.models = [] # supported
        self.get_llm_models()

        logger.info(f"model={self.openai_model_name}, max_tokens={max_tokens}")

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

    def build_parameters_for_chat(self, messages, stream=False):
        params = dict(
            model=self.openai_model_name,
            messages=messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            top_p=self.top_p,
            frequency_penalty=self.frequency_penalty,
            n=1,
            stop=None,
            stream=stream,
        )
        return params

    def call_llm_model(self, messages):
        self.tokenStat.add_msgs(messages)

        response = self.chat_model.create(
            **self.build_parameters_for_chat(messages)
        )

        self.tokenStat.output_token_stat()

        full_content = response.choices[0].message.content
        if full_content is None:
            raise TypeError("no response")
        full_content = full_content.strip()
        self.send_content(full_content)

        return full_content

    def call_llm_model_by_stream(self, messages):
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

        return full_content.strip()

    def chat(self, messages, for_raw=False, for_stream=False):
        """ return list_dict """
        retry_times = 10
        err_count_map = {}
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
                continue

        raise Exception("chat to LLM is failed")
