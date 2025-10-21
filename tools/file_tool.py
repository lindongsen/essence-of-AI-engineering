'''
  Author: DawsonLin
  Email: lin_dongsen@126.com
  Created: 2025-10-18
  Purpose:
'''

import os

from context import ctx_safe

# lower of letter
WHITE_LIST_NO_TRUNCATE_EXT = [
    # flags
    "done", "whole",
    # settings
    "md", "manifest", "conf", "yaml", "config", "cfg", "rc", "cnf", "xml", "pem", "json",
    # devlang
    "py", "go", "c", "c++", "sh", "cmd",
]

def write_file(file_path:str, content:str):
    """ write content to file.

    # parameters
    :file_path: string, the file path;
    :content: string

    # return, bool
    True for ok, False for error.
    """
    try:
        with open(file_path, "w+") as fd:
            fd.write(content)
    except Exception as _:
        return False
    return True

def read_file(file_path:str, seek:int=0, size:int=-1):
    """ read a file and output file content.

    # parameters
    :file_path: string, the file path;
    :seek: int, read from this offset, default is 0;
    :size: int, -1 for all, default is -1;

    # return
    string for ok, None for failed.

    # attention
    - When it is explicitly required to read the complete file, these parameters are not needed: seek, size.
    """
    file_path_lower = file_path.lower()
    file_ext = file_path_lower.rsplit('.', 1)[-1]

    try:
        with open(file_path, "r") as fd:
            fd.seek(seek)
            content = fd.read(size)

            # context limit
            if file_ext in WHITE_LIST_NO_TRUNCATE_EXT:
                pass
            else:
                content = ctx_safe.truncate_message(content)

            return content
    except Exception as _:
        return None

def append_file(file_path: str, content: str) -> bool:
    """ append content to file.

    # parameters
    :file_path: string, the file path;
    :content: string

    # return, bool
    True for ok, False for error.
    """
    try:
        with open(file_path, "a+") as fd:
            fd.write(content)
    except Exception as _:
        return False
    return True

def exists_file(file_path:str):
    """ check the file or folder if exists.

    # parameters
    :file_path: string

    # return
    bool, True for existing.
    """
    return os.path.exists(file_path)


TOOLS = dict(
    write_file=write_file,
    read_file=read_file,
    exists_file=exists_file,
    append_file=append_file,
)
