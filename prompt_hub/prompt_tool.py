'''
  Author: DawsonLin
  Email: lin_dongsen@126.com
  Created: 2025-10-20
  Purpose:
'''

import os

def read_prompt(relative_path):
    """ return string for file content.

    :relative_path: e.g. 'format/json.md'
    """
    file_path = os.path.join(
        os.path.dirname(__file__), relative_path
    )
    with open(file_path) as fd:
        content = fd.read().strip()
        if content:
            # add split line to tail
            if content.endswith("====") or content.endswith("----"):
                content += "\n"
            else:
                content += "\n----\n\n"
            return content

    return ""
