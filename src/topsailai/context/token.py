'''
  Author: DawsonLin
  Email: lin_dongsen@126.com
  Created: 2025-10-22
  Purpose:
'''

import time
import threading

import tiktoken

from topsailai.logger.log_chat import logger
from topsailai.utils.print_tool import print_step


def count_tokens(text, encoding_name="cl100k_base"):
    """
    计算文本的token数量

    Args:
        text (str): 要计算token的文本
        encoding_name (str): 编码器名称，默认为cl100k_base

    Returns:
        int: token数量
    """
    try:
        # 获取编码器
        encoding = tiktoken.get_encoding(encoding_name)

        # 编码文本并计算token数量
        tokens = encoding.encode(text)
        return len(tokens)

    except Exception as e:
        logger.warning(f"failed to count tokens: {e}")
        return 0

def count_tokens_for_model(text, model_name="gpt-4"):
    """
    为特定模型计算token数量

    Args:
        text (str): 要计算token的文本
        model_name (str): 模型名称

    Returns:
        int: token数量
    """
    try:
        # 获取模型的编码器
        encoding = tiktoken.encoding_for_model(model_name)

        # 编码文本并计算token数量
        tokens = encoding.encode(text)
        return len(tokens)

    except Exception as e:
        logger.warning(f"failed to count tokens: {e}")
        return 0


class TokenStat(threading.Thread):
    """ tracking token stat """
    def __init__(self, llm_id:str, lifetime:int=86400):
        """ define keys.

        :lifetime: seconds, it <= 0 for forever.
        """
        self._start_time = int(time.time())
        self._end_time = 0
        if lifetime > 0:
            self._end_time = self._start_time + lifetime + 60
        self._last_msg_time = 0

        super(TokenStat, self).__init__(name=f"TokenStat:{llm_id}", daemon=1)
        self.total_count = 0
        self.current_count = 0

        self.total_text_len = 0
        self.current_text_len = 0

        self.msg_count = 0

        self.buffer = None
        self.rlock = threading.RLock()

        self.flag_running = True
        self.start()


    def output_token_stat(self):
        """ output stat """
        with self.rlock:
            info = dict(
                total_count=self.total_count,
                current_count=self.current_count,
                total_text_len=self.total_text_len,
                current_text_len=self.current_text_len,
                msg_count=self.msg_count,
            )
        msg = f"[token_stat] {info}"
        print_step(msg)
        logger.info(msg)
        return

    def add_msgs(self, msgs):
        """ the msgs will be sent to LLM, save it to buffer for token calc """
        with self.rlock:
            self.buffer = msgs

            self.msg_count = len(msgs)
            self.current_count = 0
            self.current_text_len = 0

            self._last_msg_time = int(time.time())

    def run(self):
        self.flag_running = True

        # control frequence
        count_freq = 0
        need_freq = False
        if self._end_time:
            need_freq = True

        # idle time
        max_idle_time = 600

        def check():
            """ return bool """

            # check lifetime
            if self._end_time:
                now_ts = int(time.time())
                if self._end_time < now_ts:
                    # end life
                    if now_ts - self._last_msg_time > max_idle_time:
                        logger.info("quit due to lifetime is reached")
                        return False
                    # LLM may be using by some tools.

            return True

        while self.flag_running:

            if need_freq:
                count_freq += 1
                # interval is 10 second.
                if count_freq > 1000:
                    count_freq = 0
                    if not check():
                        break

            time.sleep(0.01)
            buffer = self.buffer
            if not buffer:
                continue

            with self.rlock:
                self.buffer = None

                if not isinstance(buffer, str):
                    buffer = str(buffer)

                self.current_text_len = len(buffer)
                self.current_count = count_tokens(buffer)
                self.total_count += self.current_count
                self.total_text_len += self.current_text_len

        logger.info(f"TokenStat is exited: {self.name}")
