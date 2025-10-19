import os
import subprocess

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
        result = subprocess.run(cmd_string, env=env, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        # return tuple(returncode, stdout, stderr)
        return (result.returncode, result.stdout.strip(), result.stderr.strip())
    except subprocess.CalledProcessError as e:
        return (e.returncode, "", e.stderr.strip())

# name: func
TOOLS = dict(
    exec_cmd=exec_cmd,
)
