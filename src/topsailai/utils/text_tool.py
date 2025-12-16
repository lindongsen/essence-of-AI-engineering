'''
  Author: DawsonLin
  Email: lin_dongsen@126.com
  Created: 2025-10-20
  Purpose: Text processing and encoding utilities
'''

import chardet


def safe_decode(data):
    """Safely decode bytes to string with automatic encoding detection.

    This function attempts to decode bytes data to a string using automatic
    encoding detection. If the detected encoding fails, it falls back to
    UTF-8 with error replacement.

    Args:
        data: Input data to decode (bytes or string)

    Returns:
        str: Decoded string

    Note:
        - If input is already a string, returns it unchanged
        - If input is empty or None, returns empty string
        - Uses chardet for encoding detection with UTF-8 fallback
        - Uses 'replace' error handling to avoid decoding failures
    """
    if isinstance(data, str):
        return data

    if not data:
        return ""

    # Detect encoding
    detected = chardet.detect(data)
    encoding = detected.get('encoding', 'utf-8')

    if not encoding:
        try:
            return data.decode('utf-8', errors='replace')
        except Exception:
            return str(data)

    try:
        return data.decode(encoding)
    except UnicodeDecodeError:
        # Fallback to UTF-8 with error replacement
        return data.decode('utf-8', errors='replace')
