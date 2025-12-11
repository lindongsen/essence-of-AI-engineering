'''
  Author: DawsonLin
  Email: lin_dongsen@126.com
  Created: 2025-12-10
  Purpose:
'''

import os
import socket
import subprocess

from .text_tool import safe_decode


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

def exec_cmd(cmd_string:str, no_need_stderr:bool=False, timeout:int=None):
    """ execute command line

    Args:
        cmd_string (str): command line string
        no_need_stderr (bool): if True, set stderr to "". Defaults to False.

    Returns:
        tuple: (code, stdout, stderr)
    """
    env = build_env()
    result = subprocess.run(
        cmd_string,
        env=env,
        shell=True,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=False,
        timeout=timeout,
    )
    return (
        result.returncode,
        safe_decode(result.stdout),
        "" if no_need_stderr else safe_decode(result.stderr),
    )

def exec_cmd_in_remote(cmd:str, remote:str, port=22, timeout:int=None):
    """execute command in remote host

    Args:
        cmd (str): command line
        remote (str): remote host
        timeout (int, optional): timeout seconds. Defaults to None(no timeout).

    Returns:
        tuple: (code, stdout, stderr)
    """
    assert cmd
    if not remote \
        or remote in ["localhost", "local", "127.0.0.1", socket.gethostname()]:
        return exec_cmd(cmd)

    options = (
        "-o 'StrictHostKeyChecking no' "
        "-o 'UserKnownHostsFile /dev/null' "
        "-o ConnectTimeout=10 "
        "-o ConnectionAttempts=3 "
    )
    if port:
        options += f"-p {port}"

    cmd_ssh = f"cat << EOF | ssh {options} root@{remote} bash -s\n{cmd}\nEOF"
    return exec_cmd(cmd_ssh, timeout=timeout)
