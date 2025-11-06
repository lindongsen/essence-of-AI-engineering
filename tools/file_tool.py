'''
  Author: DawsonLin
  Email: lin_dongsen@126.com
  Created: 2025-10-18
  Purpose:
'''

# pylint: disable=C0209

import os
import traceback

from context import ctx_safe
from utils import text_tool
from utils import print_tool

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

def _do_step_read_bytes(fd, size:int):
    """ read in a certain block size order.

    return bytes.
    """
    offset = 1024

    if size > 0 and size <= offset:
        return fd.read(size)

    content = b""
    count = 0
    while True:
        _data = fd.read(offset)
        if not _data:
            break
        content += _data
        count += offset

        if size > 0:
            if count >= size:
                break
            remaining_size = size - count
            if remaining_size <= offset:
                content += fd.read(remaining_size)
                return content

        if ctx_safe.is_need_truncate(count):
            break
    if size > 0:
        return content[:size]
    return content

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
    - When the file extension is not in white list, the file reading process may be (force to truncate).
      - white list: {WHITE_LIST_NO_TRUNCATE_EXT}
    """.format(
        WHITE_LIST_NO_TRUNCATE_EXT=WHITE_LIST_NO_TRUNCATE_EXT,
    )
    file_path_lower = file_path.lower()
    file_ext = file_path_lower.rsplit('.', 1)[-1]

    try:
        with open(file_path, "rb") as fd:
            if seek < 0:
                fd.seek(seek, 2)
            else:
                fd.seek(seek)

            if file_ext not in WHITE_LIST_NO_TRUNCATE_EXT:
                content = _do_step_read_bytes(fd, size)
                content = ctx_safe.truncate_message(content)
            else:
                content = fd.read(size)
            content = text_tool.safe_decode(content)

            # context limit
            if file_ext in WHITE_LIST_NO_TRUNCATE_EXT:
                pass
            else:
                content = ctx_safe.truncate_message(content)

            return content
    except Exception:
        print_tool.print_error(traceback.format_exc())
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
    :file_path: string, one file or one folder.

    # return
    bool, True for existing.
    """
    return os.path.exists(file_path)

def check_files_existing(**files):
    """ check multiple files or folders if exist.

    # parameters
    :**files: keyword arguments, each key is a name (string), value is the file or folder path (string) to check existence.

    # return
    dict of str to bool, where keys are the provided names, values are True if the path exists, False otherwise.

    # Example
        exist_files(
            file1="path1",
            file2="path2",
            ...
        )
    """
    results = {}
    for fname, fpath in files.items():
        results[fname] = os.path.exists(fpath)
    return results


TOOLS = dict(
    write_file=write_file,
    read_file=read_file,
    exists_file=exists_file,
    append_file=append_file,
    check_files_existing=check_files_existing,
)
