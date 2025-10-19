'''
  Author: DawsonLin
  Email: lin_dongsen@126.com
  Created: 2025-10-18
  Purpose:
'''

import os

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

def read_file(file_path:str):
    """ read a file and output file content.

    # parameters
    :file_path: string, the file path;

    # return
    string for ok, None for failed.
    """
    try:
        with open(file_path, "r") as fd:
            return fd.read()
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
    """ check the file if exists.

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
