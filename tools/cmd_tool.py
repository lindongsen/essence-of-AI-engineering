import subprocess

def exec_cmd(cmd_string):
    """
    # parameters
    :cmd_string: cmd line.

    # return
    tuple(code, stdout, stderr)
    """
    try:
        result = subprocess.run(cmd_string, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        # return tuple(returncode, stdout, stderr)
        return (result.returncode, result.stdout.strip(), result.stderr.strip())
    except subprocess.CalledProcessError as e:
        return (e.returncode, "", e.stderr.strip())

# name: func
TOOLS = dict(
    exec_cmd=exec_cmd,
)
