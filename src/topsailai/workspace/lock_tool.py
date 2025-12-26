'''
  Author: DawsonLin
  Email: lin_dongsen@126.com
  Created: 2025-12-26
  Purpose: Provides file locking functionality for thread-safe operations
'''

import os
from contextlib import contextmanager

from topsailai.utils.file_tool import (
    ctxm_file_lock,
)

from . import folder_constants


def init():
    """
    Initialize the lock directory structure.

    This function ensures that the lock directory specified by FOLDER_LOCK
    exists. If the directory doesn't exist, it will be created.

    Note: This function is called automatically when the module is imported.

    Returns:
        None
    """
    os.makedirs(folder_constants.FOLDER_LOCK, exist_ok=True)


# Initialize lock directory on module import
init()


@contextmanager
def FileLock(name: str):
    """
    Context manager for file-based locking.

    This function provides a thread-safe file locking mechanism using
    the underlying ctxm_file_lock utility. It automatically handles
    lock file creation, acquisition, and release.

    Args:
        name (str): The name of the lock. If the name doesn't end with
                   ".lock", the extension will be automatically added.
                   The lock file will be created in the FOLDER_LOCK directory.

    Yields:
        fd: A file descriptor (writeable) representing the acquired lock.

    Raises:
        AssertionError: If the name parameter is empty or None.

    Example:
        >>> with FileLock("my_resource"):
        ...     # Critical section - only one process can execute this at a time
        ...     perform_thread_safe_operation()

    Note:
        - The lock file is automatically managed and does not need to be
          manually deleted
        - This uses file-based locking which works across processes
        - The lock is released automatically when exiting the context
    """
    # Validate that the lock name is provided
    assert name, "Lock name cannot be empty"

    # Ensure the lock name has the correct extension
    if not name.endswith(".lock"):
        name += ".lock"

    # Construct the full path to the lock file
    file_path = folder_constants.FOLDER_LOCK + "/" + name

    # Acquire the lock and yield control to the critical section
    with ctxm_file_lock(file_path) as fd:
        yield fd

    # Lock is automatically released when context exits
    # No need to manually delete the lock file
    return
