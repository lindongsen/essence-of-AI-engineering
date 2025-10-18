'''
  Author: DawsonLin
  Email: lin_dongsen@126.com
  Created: 2025-10-18
  Purpose:
'''

def to_list(v, to_ignore_none=False):
    """ format the value to list """
    if isinstance(v, (list, set, tuple)):
        return list(v)
    if v is None:
        if to_ignore_none:
            return v
    return [v]
