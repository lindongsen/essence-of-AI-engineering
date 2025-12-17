'''
  Author: DawsonLin
  Email: lin_dongsen@126.com
  Created: 2025-10-18
  Purpose: Utility functions for data formatting and conversion
'''

import re
import simplejson
from collections import OrderedDict

from .json_tool import safe_json_dump


TOPSAILAI_FORMAT_PREFIX = "topsailai."


def to_list(v, to_ignore_none=False):
    """Convert a value to a list, handling various input types.

    This function converts different data types to a list format. It handles
    lists, sets, tuples, None values, and single values appropriately.

    Args:
        v: Value to convert to list
        to_ignore_none: If True and v is None, returns None instead of [None]

    Returns:
        list or None: Converted list, or None if to_ignore_none is True and v is None

    Examples:
        to_list([1, 2, 3]) -> [1, 2, 3]
        to_list((1, 2, 3)) -> [1, 2, 3]
        to_list({1, 2, 3}) -> [1, 2, 3]
        to_list(42) -> [42]
        to_list(None) -> [None]
        to_list(None, to_ignore_none=True) -> None
    """
    if isinstance(v, (list, set, tuple)):
        return list(v)
    if v is None:
        if to_ignore_none:
            return v
    return [v]

def parse_topsailai_format(text: str) -> dict:
    """
    Parse text in the topsailai format.

    Format:
    topsailai.{step_name}
    {raw_text}

    Returns a dictionary where keys are step names and values are raw text content.
    """
    lines = text.strip().split('\n')
    if not lines:
        return {}

    result = OrderedDict()
    current_step = None
    current_content = []

    for line in lines:
        # Check if line starts a new step
        if line.startswith(TOPSAILAI_FORMAT_PREFIX):
            # Save previous step if exists
            if current_step:
                result[current_step] = '\n'.join(current_content).strip()

            # Start new step
            step_name = line[len(TOPSAILAI_FORMAT_PREFIX):].strip()
            current_step = step_name
            current_content = []
        elif current_step:
            # Add to current step's content
            current_content.append(line)

    # Don't forget the last step
    if current_step:
        result[current_step] = '\n'.join(current_content).strip()

    return result

def parse_topsailai_format_regex(text: str) -> dict:
    """
    Parse text in the topsailai format using regex.
    """
    pattern = r'topsailai\.(\w+)\n(.*?)(?=\ntopsailai\.|\Z)'
    matches = re.findall(pattern, text, re.DOTALL)

    result = OrderedDict()
    for step_name, content in matches:
        result[step_name] = content.strip()

    return result

def format_dict_to_list(d:dict, key_name:str, value_name:str) -> list[dict]:
    """ format dict to list_dict """
    if not d:
        return []

    result = []
    for k, v in d.items():
        result.append(
            {
                key_name: k,
                value_name: v,
            }
        )
    return result

def to_topsailai_format(content:str|list|dict, key_name:str, value_name:str, for_print=False) -> str:
    if isinstance(content, str):
        if key_name not in content:
            return content
        content = simplejson.loads(content)

    result = ""
    for d in to_list(content):
        # d is dict
        # keywords:
        #   step_name
        #   raw_text
        #   tool_call ...
        result += f"{TOPSAILAI_FORMAT_PREFIX}{d[key_name]}\n"
        del d[key_name]
        if value_name in d:
            v = d[value_name]
            if for_print:
                if isinstance(v, (list, dict)):
                    v = safe_json_dump(v)
            result += f"{v}\n"
            del d[value_name]
        if d:
            result += safe_json_dump(d) + "\n"
        result += "\n"
    return result
