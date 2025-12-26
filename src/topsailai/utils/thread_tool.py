'''
  Author: DawsonLin
  Email: lin_dongsen@126.com
  Created: 2025-11-05
  Purpose:
'''

import threading

def wait_thrs(thrs: list):
    """
    Wait for all threads in the list to finish execution.

    Args:
        thrs (list): List of threading.Thread objects to wait for
    """
    for thread in thrs:
        thread.join()
    return

def is_main_thread():
    """Check if the current thread is the main thread.

    Returns:
        bool: True if the current thread is the main thread, False otherwise.

    Example:
        >>> threading.Thread(target=lambda : print(is_main_thread())).start()
        False
    """
    """ return bool.

    Example:
        >>> threading.Thread(target=lambda : print(is_main_thread())).start()
        False
    """
    return threading.current_thread() is threading.main_thread()
