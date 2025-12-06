import threading
from contextlib import contextmanager

# Define static variables for thread-local storage keys
KEY_AGENT_NAME = "agent_name"
KEY_SESSION_ID = "session_id"
KEY_AGENT_OBJECT = "agent_object"

# Define a thread-local storage object
g_thr_local = threading.local()

# Limit the depth of recursive calls for agent.
MAX_AGENT_DEEP = 3
KEY_AGENT_DEEP = "agent_deep" # value is number for count


def set_thread_var(name, value):
    """Set a variable in thread-local storage.

    Args:
        name: Variable name to set
        value: Value to store
    """
    setattr(g_thr_local, name, value)
    return

def rid_all_thread_vars():
    """Remove all variables from thread-local storage.

    This clears all thread-specific data, useful for cleanup
    when a thread is being reused or terminated.
    """
    for k in list(g_thr_local.__dict__.keys()):
        delattr(g_thr_local, k)
    return

def get_thread_var(name, default=None):
    """Get a variable from thread-local storage.

    Args:
        name: Variable name to retrieve
        default: Default value if variable doesn't exist

    Returns:
        The stored value or default if not found
    """
    return getattr(g_thr_local, name, default)

def unset_thread_var(name):
    """Remove a specific variable from thread-local storage.

    Args:
        name: Variable name to remove
    """
    if hasattr(g_thr_local, name):
        delattr(g_thr_local, name)
    return

def incr_agent_deep():
    """ increase deep +1 """
    v = get_thread_var(KEY_AGENT_DEEP, 0) or 0
    v += 1
    set_thread_var(KEY_AGENT_DEEP, v)
    return

def decr_agent_deep():
    """ decrease deep -1 """
    v = get_thread_var(KEY_AGENT_DEEP, 0) or 0
    if v > 0:
        v -= 1
        set_thread_var(KEY_AGENT_DEEP, v)
    return

@contextmanager
def ctxm_give_agent_name(agent_name):
    """Context manager to temporarily set agent name in thread-local storage.

    This context manager sets the agent name for the duration of the context
    and automatically restores the previous value when exiting.

    Args:
        agent_name: Agent name to set temporarily

    Example:
        with ctxm_give_agent_name("my_agent"):
            # Code that uses the agent name
            print(get_agent_name())  # Output: "my_agent"
    """
    old_agent_name = get_thread_var(KEY_AGENT_NAME)
    set_thread_var(KEY_AGENT_NAME, agent_name)
    try:
        yield
    finally:
        if old_agent_name:
            set_thread_var(KEY_AGENT_NAME, old_agent_name)
        else:
            unset_thread_var(KEY_AGENT_NAME)
    return

def get_agent_name():
    """Get the current agent name from thread-local storage.

    Returns:
        str: Current agent name, or None if not set
    """
    return get_thread_var(KEY_AGENT_NAME)

def get_session_id():
    """Get the current session ID from thread-local storage.

    Returns:
        str: Session ID as string, or None if not set
    """
    return str(get_thread_var(KEY_SESSION_ID))

@contextmanager
def ctxm_set_agent(agent_obj):
    """Context manager to temporarily set agent object in thread-local storage.

    This context manager sets the agent object for the duration of the context
    and automatically restores the previous value when exiting.

    Args:
        agent_obj: Agent object to set temporarily

    Example:
        with ctxm_set_agent(my_agent):
            # Code that uses the agent object
            agent = get_agent_object()
    """
    assert get_thread_var(KEY_AGENT_DEEP, 0) < MAX_AGENT_DEEP, \
        f"Reach the maximum depth: {MAX_AGENT_DEEP}"

    old_agent_obj = get_thread_var(KEY_AGENT_OBJECT)
    set_thread_var(KEY_AGENT_OBJECT, agent_obj)
    try:
        incr_agent_deep()
        yield
    finally:
        decr_agent_deep()
        if old_agent_obj:
            set_thread_var(KEY_AGENT_OBJECT, old_agent_obj)
        else:
            unset_thread_var(KEY_AGENT_OBJECT)
    return

def get_agent_object():
    """Get the current agent object from thread-local storage.

    Returns:
        object: Current agent object, or None if not set
    """
    return get_thread_var(KEY_AGENT_OBJECT)
