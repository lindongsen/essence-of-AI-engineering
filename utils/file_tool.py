'''
  Author: DawsonLin
  Email: lin_dongsen@126.com
  Created: 2025-10-17
  Purpose:
'''

from pathlib import Path

def get_filename(file_path: str) -> str:
    """Get the file name (without the final extension) from a path.

    Examples:
        "/tmp/123.txt" -> "123"
        "C:\\data\\report.pdf" -> "report"

    Args:
        file_path: Path to the file.

    Returns:
        Filename without its final suffix, or an empty string for falsy input.
    """
    if not file_path:
        return ""
    return Path(file_path).stem
