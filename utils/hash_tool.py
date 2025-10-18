'''
  Author: DawsonLin
  Email: lin_dongsen@126.com
  Created: 2025-10-17
  Purpose:
'''

import hashlib

def md5sum(s: str | bytes) -> str:
    """Return the MD5 hex digest of a string or bytes.

    Args:
        s: Input text or bytes to hash.

    Returns:
        Hexadecimal MD5 digest.
    """

    if isinstance(s, str):
        b = s.encode("utf-8")
    else:
        b = s
    return hashlib.md5(b).hexdigest()