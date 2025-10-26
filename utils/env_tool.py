'''
  Author: DawsonLin
  Email: lin_dongsen@126.com
  Created: 2025-10-27
  Purpose:
'''

import os

def is_debug_mode():
    """ return bool. True for debug mode """
    if os.getenv("DEBUG", "0") == "0":
        return False
    return True
