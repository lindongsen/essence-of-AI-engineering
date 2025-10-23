'''
  Author: DawsonLin
  Email: lin_dongsen@126.com
  Created: 2025-10-23
  Purpose:
'''

import os
import re

from .log_tool import logger


SENTENCE_SPLIT_CHARS = list("。！？.!?")
BRACKET_STRINGS = "([{<（【《"
BRACKET_STRINGS_2 = ")]}>）】》"
BRACKET_STRINGS_2_SEPARATORS = [f"{k}\n" for k in BRACKET_STRINGS_2]


def recognize_separators(text:str):
    """ recognize separators to truncate text """
    separators = []
    for k in BRACKET_STRINGS_2_SEPARATORS:
        if k in text:
            separators.append(k)
    return separators

def split_sentence(text:str):
    """ return sentences """
    #sentences = sent_tokenize(text)
    sentences = re.split(r'(?<=[。！？.!?])', text)
    return sentences

def format_separators(separators:list):
    """
    # args
    :separators: list_str
    """
    if not separators:
        return None
    new_separators = []
    for s in separators:
        s = s.replace("\\n", "\n").replace("\\t", "\t")
        new_separators.append(s)
    return new_separators

def match_separators(line:str, separators:list):
    """ return True for matched """
    if not line or not separators:
        return False

    line_strip = line.strip()
    if not line_strip:
        return False

    for separator_str in separators:
        if not separator_str:
            continue
        if line.endswith(separator_str):
            return True

        separator_str_strip = separator_str.strip()

        # case: ")   \n", [first char, space, space, space, \n]
        if len(separator_str_strip) == 1 \
            and separator_str_strip == separator_str[0] \
            and line_strip[-1] == separator_str_strip \
            and line[-1] == separator_str[-1]:
            return True
    # end for
    return False

class IterChunks(object):
    """ iter string for chunk by stream to read file. """
    def __init__(self, file_path, chunk_size=1000, separators:list=None):
        self.file_path = file_path
        self.file_size = os.path.getsize(file_path)
        self.chunk_size = chunk_size
        self.max_chunk_size = chunk_size + 1000
        self.separators = format_separators(separators)

        self.fd = open(file_path, mode="r", encoding="utf-8")

        self.stat_chunk_count = 0
        self.stat_current_seek = 0
        return

    def __del__(self):
        try:
            self.fd.close()
        except Exception:
            pass

    def __iter__(self):
        return self

    def __next__(self):
        content = self.get_chunk().strip()
        content_size = len(content)
        self.stat_chunk_count += 1
        self.stat_current_seek += content_size

        percent = round(self.stat_current_seek/self.file_size*100, 2)
        logger.info(
            "iter chunk progress: " +
            f"file={self.file_path}, chunk_count={self.stat_chunk_count}, " +
            f"current_seek={self.stat_current_seek}, content_size={content_size}, " +
            f"progress={percent}%"
        )
        return content

    def get_chunk(self):
        """ return string for chunk """
        s = self.fd.readline()
        if not s:
            self.fd.close()
            raise StopIteration

        if len(s) > self.chunk_size:
            if not s.strip():
                s = "\n"
            else:
                return s

        count = 0
        while True:
            count += 1
            line = self.fd.readline()
            if not line:
                break

            line_strip = line.strip()

            # misc
            if not line_strip:
                if s[-1] in SENTENCE_SPLIT_CHARS:
                    s += line
                continue
            elif len(line_strip) <= 7:
                # case: (...)
                if line_strip[0] in BRACKET_STRINGS:
                    pass
                elif line_strip[0] in ["'", '"', '`', '-', '+', '=', '_', '#', '@', '*', '/', '\\']:
                    pass
                else:
                    s += line_strip + ";"
            elif line_strip[-1] not in SENTENCE_SPLIT_CHARS:
                if s.endswith(line_strip):
                    s += "," + line_strip
                else:
                    s += line_strip
            else:
                s += line

            # too small size
            if not s.strip():
                s = "\n"
                continue
            if len(s) < 100:
                continue

            # separators1
            if match_separators(line, self.separators):
                break
            # separators2
            if match_separators(line, BRACKET_STRINGS_2_SEPARATORS):
                break

            # too large size

            ## normal size
            if len(s) > self.chunk_size:
                if line_strip == "":
                    break
                elif count == 1:
                    break

            ## force to truncate
            if len(s) > self.max_chunk_size:
                break

        # end while
        return s
