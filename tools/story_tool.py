'''
  Author: DawsonLin
  Email: lin_dongsen@126.com
  Created: 2025-11-24
  Purpose:
'''

import os

from utils import (
    time_tool,
    file_tool,
)

KEY_STORY = "story"

def get_story_file(workspace:str, story_id:str):
    """get a file path for the story content.

    Args:
        workspace (str): folder path.
        story_id (str): story id.

    Return:
        str, a file path.
        none, failed to get file.
    """
    story_folder = os.path.join(workspace, KEY_STORY)
    files = file_tool.find_files_by_name(story_folder, story_id)
    if files:
        return files[0]
    return None

def write_story_to_file(workspace:str, story_id:str, story_content:str):
    """write story content to file.

    Args:
        workspace (str): folder path.
        story_id (str): story id.
        story_content (str): story content.

    Return:
        str, a filepath of this story storing.
        other, failed to write.
    """
    folder_path = os.path.join(workspace, KEY_STORY, time_tool.get_current_day())
    file_path = os.path.join(folder_path, story_id)
    os.makedirs(folder_path, exist_ok=True)
    with open(file_path, "w+", encoding="utf-8") as fd:
        fd.write(story_content)
    return file_path

def read_story_from_file(workspace:str, story_id:str):
    """ Automatically locate the story file from the workspace based on the story ID,
    and read the file content.

    Args:
        workspace (str): folder path.
        story_id (str): story id.

    Return:
      str, story content.
      none, no found story.
    """
    story_file = get_story_file(workspace, story_id)
    if not story_file:
        return None
    with open(story_file, encoding='utf-8') as fd:
        return fd.read(story_file)
    return None


TOOLS = dict(
    write_story_to_file=write_story_to_file,
    read_story_from_file=read_story_from_file,
)
