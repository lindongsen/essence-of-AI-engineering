'''
  Author: DawsonLin
  Email: lin_dongsen@126.com
  Created: 2025-12-26
  Purpose:
'''

import os
from contextlib import contextmanager

from topsailai.utils.file_tool import (
    ctxm_file_lock,
)

from . import folder_constants

def init():
    os.makedirs(folder_constants.FOLDER_LOCK, exist_ok=True)

init()

@contextmanager
def FileLock(name:str):
    """ yield fd (writeable)"""
    assert name
    if not name.endswith(".lock"):
        name += ".lock"
    file_path = folder_constants.FOLDER_LOCK + "/" + name
    with ctxm_file_lock(file_path) as fd:
        yield fd
    # DONOT NEED DELETE LOCK FILE
    return
