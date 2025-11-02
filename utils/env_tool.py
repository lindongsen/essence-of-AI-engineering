'''
  Author: DawsonLin
  Email: lin_dongsen@126.com
  Created: 2025-10-27
  Purpose: Environment variable utilities and configuration helpers
'''

import os

def is_debug_mode():
    """Check if the application is running in debug mode.
    
    Debug mode is determined by the DEBUG environment variable:
    - DEBUG="0" or not set: Production mode (returns False)
    - DEBUG="1" or any other value: Debug mode (returns True)
    
    Returns:
        bool: True if debug mode is enabled, False otherwise
    """
    if os.getenv("DEBUG", "0") == "0":
        return False
    return True
