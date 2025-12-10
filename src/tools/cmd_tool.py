from utils.text_tool import safe_decode
from utils.cmd_tool import exec_cmd as exec_command
from context import ctx_safe

def format_text(s, need_truncate=True):
    """ decode and truncate

    :s: str/bytes
    """
    s = safe_decode(s).strip()
    if need_truncate:
        s = ctx_safe.truncate_message(s).strip()
    return s

def _need_whole_stdout(cmd_string:str):
    """ some cases need stdout """

    # curl wikipedia.org
    if cmd_string.startswith("curl "):
        for key in [
            "wikipedia.org",
        ]:
            if key in cmd_string:
                return True

    return False

def _format_return(cmd_string: str, t:tuple):
    """ truncate text for stdout and stderr """
    need_truncate = True
    if _need_whole_stdout(cmd_string):
        need_truncate = False
    return (t[0], format_text(t[1], need_truncate=need_truncate), format_text(t[2]))

def format_return(cmd_string:str, t:tuple):
    """ hack result """
    # no need stderr
    for tool in [
        "curl", "wget",
        "uv add", "uv sync",
        "pip install",
    ]:
        if not t[2]:
            break
        if cmd_string.startswith(tool + " "):
            t = (t[0], t[1], "")
            return _format_return(cmd_string, t)

    return _format_return(cmd_string, t)

def exec_cmd(cmd_string:str, no_need_stderr:bool=False):
    """ execute command

    Args:
        cmd_string (str):
        no_need_stderr (bool, optional): if True, stderr still be null. Defaults to False.

    Returns:
        tuple: (code, stdout, stderr)
    """
    result = exec_command(
        cmd_string,
        no_need_stderr=no_need_stderr,
    )

    return format_return(cmd_string, result)

# name: func
TOOLS = dict(
    exec_cmd=exec_cmd,
)
