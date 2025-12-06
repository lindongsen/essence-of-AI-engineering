'''
  Author: DawsonLin
  Email: lin_dongsen@126.com
  Created: 2025-10-18
  Purpose: Utility functions for data formatting and conversion
'''

def to_list(v, to_ignore_none=False):
    """Convert a value to a list, handling various input types.
    
    This function converts different data types to a list format. It handles
    lists, sets, tuples, None values, and single values appropriately.

    Args:
        v: Value to convert to list
        to_ignore_none: If True and v is None, returns None instead of [None]

    Returns:
        list or None: Converted list, or None if to_ignore_none is True and v is None

    Examples:
        to_list([1, 2, 3]) -> [1, 2, 3]
        to_list((1, 2, 3)) -> [1, 2, 3]
        to_list({1, 2, 3}) -> [1, 2, 3]
        to_list(42) -> [42]
        to_list(None) -> [None]
        to_list(None, to_ignore_none=True) -> None
    """
    if isinstance(v, (list, set, tuple)):
        return list(v)
    if v is None:
        if to_ignore_none:
            return v
    return [v]
