import os
import subprocess

from utils.text_tool import safe_decode
from context import ctx_safe

def format_text(s):
    """ decode and truncate

    :s: str/bytes
    """
    s = safe_decode(s).strip()
    s = ctx_safe.truncate_message(s).strip()
    return s

def build_env(d:dict=None):
    """ build environs, return dict. """
    env = {}
    for k in ["PYTHONPATH", "PATH", "HOSTNAME", "SHELL"]:
        v = os.getenv(k)
        if v:
            env[k] = v
    if d:
        env.update(d)
    return env

def _format_return(t:tuple):
    """ truncate text for stdout and stderr """
    return (t[0], format_text(t[1]), format_text(t[2]))

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
            return _format_return(t)

    return _format_return(t)

def exec_cmd(cmd_string, no_need_stderr=False):
    """
    # parameters
    :cmd_string: cmd line.
    :no_need_stderr: bool; if True, stderr will be null string; default is False for raw content.

    # return
    tuple(code, stdout, stderr)
    """
    env = build_env()
    t = None
    try:
        result = subprocess.run(cmd_string, env=env, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=False)
        # return tuple(returncode, stdout, stderr)
        t = (
            result.returncode,
            result.stdout,
            "" if no_need_stderr else result.stderr
        )
    except subprocess.CalledProcessError as e:
        t = (
            e.returncode,
            e.stdout,
            "" if no_need_stderr else e.stderr
        )

    return format_return(cmd_string, t)

# name: func
TOOLS = dict(
    exec_cmd=exec_cmd,
)
