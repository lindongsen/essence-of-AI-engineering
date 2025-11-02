'''
  Author: DawsonLin
  Email: lin_dongsen@126.com
  Created: 2025-10-17
  Purpose: Hashing utilities for data integrity and verification
'''

import hashlib

def md5sum(s: str | bytes) -> str:
    """Calculate the MD5 hash of a string or bytes.
    
    This function computes the MD5 hexadecimal digest of the input data.
    It automatically handles both string and bytes inputs.
    
    Args:
        s: Input data to hash (string or bytes)
    
    Returns:
        str: Hexadecimal MD5 digest string
    
    Example:
        md5sum("hello") -> "5d41402abc4b2a76b9719d911017c592"
        md5sum(b"hello") -> "5d41402abc4b2a76b9719d911017c592"
    """

    if isinstance(s, str):
        b = s.encode("utf-8")
    else:
        b = s
    return hashlib.md5(b).hexdigest()