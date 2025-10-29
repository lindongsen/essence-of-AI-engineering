import threading
from contextlib import contextmanager

# define static variables
KEY_AGENT_NAME = "agent_name"
KEY_SESSION_ID = "session_id"
KEY_AGENT_OBJECT = "agent_object"

# define a thread-local storage object
g_thr_local = threading.local()

def set_thread_var(name, value):
    setattr(g_thr_local, name, value)
    return

def rid_all_thread_vars():
    for k in list(g_thr_local.__dict__.keys()):
        delattr(g_thr_local, k)
    return

def get_thread_var(name, default=None):
    return getattr(g_thr_local, name, default)

def unset_thread_var(name):
    if hasattr(g_thr_local, name):
        delattr(g_thr_local, name)
    return

@contextmanager
def ctxm_give_agent_name(agent_name):
    """ context manager to set agent name """
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
    """ return str for agent name """
    return get_thread_var(KEY_AGENT_NAME)

def get_session_id():
    """ return  session id """
    return str(get_thread_var(KEY_SESSION_ID))

@contextmanager
def ctxm_set_agent(agent_obj):
    """ context manager to set agent object """
    old_agent_obj = get_thread_var(KEY_AGENT_OBJECT)
    set_thread_var(KEY_AGENT_OBJECT, agent_obj)
    try:
        yield
    finally:
        if old_agent_obj:
            set_thread_var(KEY_AGENT_OBJECT, old_agent_obj)
        else:
            unset_thread_var(KEY_AGENT_OBJECT)
    return

def get_agent_object():
    """ return agent object """
    return get_thread_var(KEY_AGENT_OBJECT)
