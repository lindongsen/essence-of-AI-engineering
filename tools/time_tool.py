'''
  Author: DawsonLin
  Email: lin_dongsen@126.com
  Created: 2025-10-20
  Purpose:
'''

import time

from utils.time_tool import get_current_date

def get_local_date():
    """ get current date.
    return local time in 'ISO 8601'. example: '2025-10-19T21:17:07'
    """
    return get_current_date(True)

def get_local_time():
    """ get local time in 'integer'. example: 1760908828 """
    return int(time.time())


TOOLS = dict(
    get_local_date=get_local_date,
    get_local_time=get_local_time,
)
