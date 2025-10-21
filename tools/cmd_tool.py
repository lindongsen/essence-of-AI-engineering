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

def exec_cmd(cmd_string):
    """
    # parameters
    :cmd_string: cmd line.

    # return
    tuple(code, stdout, stderr)
    """
    env = build_env()
    try:
        result = subprocess.run(cmd_string, env=env, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=False)
        # return tuple(returncode, stdout, stderr)
        return (result.returncode, format_text(result.stdout), format_text(result.stderr))
    except subprocess.CalledProcessError as e:
        return (e.returncode, "", format_text(e.stderr))

# name: func
TOOLS = dict(
    exec_cmd=exec_cmd,
)
