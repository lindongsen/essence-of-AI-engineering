'''
  Author: DawsonLin
  Email: lin_dongsen@126.com
  Created: 2025-10-19
  Purpose:
'''

from datetime import datetime

def get_current_date(with_t=False, include_ms=False):
    """
    Get the current date and time in a formatted string.

    :param with_t: If True, use 'T' as separator between date and time (ISO 8601 format).
                   Default is False, using space.
    :param include_ms: If True, include milliseconds in the time portion.
    :return: Formatted date time string.
    """
    c = " "
    if with_t:
        c = "T"
    dt = datetime.now()
    time_format = "%H:%M:%S"
    if include_ms:
        ms = f".{dt.microsecond // 1000:03d}"
        time_format += ms
    return dt.strftime(f"%Y-%m-%d{c}{time_format}")

def get_current_day():
    """
    Get the current date of day.
    e.g. 2025-11-24
    """
    dt = datetime.now()
    return dt.strftime("%Y-%m-%d")
