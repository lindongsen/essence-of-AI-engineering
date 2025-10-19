'''
  Author: DawsonLin
  Email: lin_dongsen@126.com
  Created: 2025-10-19
  Purpose:
'''

from datetime import datetime

def get_current_date(with_t=False):
    """
    :with_t: ISO 8601
    """
    c = " "
    if with_t:
        c = "T"
    return datetime.now().strftime(f"%Y-%m-%d{c}%H:%M:%S")
