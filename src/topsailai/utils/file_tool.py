'''
  Author: DawsonLin
  Email: lin_dongsen@126.com
  Created: 2025-10-17
  Purpose: File path manipulation and file system utilities
'''

import os
from pathlib import Path


##########################################################
# Core
##########################################################

def get_filename(file_path: str) -> str:
    """Extract the filename without extension from a file path.

    This function returns the stem (filename without the final extension)
    from a given file path. It handles both Unix and Windows path formats.

    Args:
        file_path: Full path to the file

    Returns:
        str: Filename without extension, or empty string for invalid input

    Examples:
        "/tmp/123.txt" -> "123"
        "C:\\data\\report.pdf" -> "report"
        "" -> ""
    """
    if not file_path:
        return ""
    return Path(file_path).stem

def match_file(
        file_path:str,
        to_exclude_dot_start:bool,
        excluded_starts:tuple,
    ) -> bool:
    if to_exclude_dot_start:
        if "/." in file_path:
            return False
        if file_path[0] == '.':
            return False

    if not excluded_starts:
        excluded_starts = tuple()

    for excluded_str_start in excluded_starts:
        if f"/{excluded_str_start}" in file_path:
            return False
        if file_path.startswith(excluded_str_start):
            return False

    return True


##########################################################
# Shell
##########################################################

def find_files_by_name(folder_path:str, file_name:str) -> list[str]:
    """get files from folder path.

    Args:
        folder_path (str): folder path
        file_name (str): file name
    """
    results = []
    for root, dirs, files in os.walk(folder_path):
        if file_name in files:
            file_path = os.path.join(root, file_name)
            results.append(file_path)

    return results

def list_files(
        folder_path:str,
        to_exclude_dot_start:bool=True,
        excluded_starts:tuple=None,
    ) -> list[str]:
    results = []
    if not excluded_starts:
        excluded_starts = tuple()

    for root, dirs, files in os.walk(folder_path):
        if not match_file(
            root,
            to_exclude_dot_start=to_exclude_dot_start,
            excluded_starts=excluded_starts,
        ):
            continue
        for file in files:
            if not match_file(
                file,
                to_exclude_dot_start=to_exclude_dot_start,
                excluded_starts=excluded_starts,
            ):
                continue
            file_path = os.path.join(root, file)
            results.append(file_path)
    return results
