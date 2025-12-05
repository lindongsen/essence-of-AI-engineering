'''
  Author: DawsonLin
  Email: lin_dongsen@126.com
  Created: 2025-10-29
  Purpose:
'''

import os

from logger import logger

from .chat_history_manager import ALL_MANAGERS
from .chat_history_manager.__base import (
    ChatHistoryBase,
)
from .session_manager.__base import (
    SessionStorageBase,
    SessionData,
)
from .session_manager.sql import SessionSQLAlchemy


def get_managers_by_env() -> list[ChatHistoryBase]:
    """ get instance of managers """
    env_ctx_history_managers = os.getenv("CONTEXT_HISTORY_MANAGERS")
    if not env_ctx_history_managers:
        return
    mgrs = []
    # "sql.ChatHistorySQLAlchemy conn=sqlite://memory.db;"
    for mgr in env_ctx_history_managers.split(';'):
        mgr = mgr.strip()
        if not mgr:
            continue
        mgr_list = mgr.split(' ')
        mgr_name = mgr_list[0]
        if mgr_name not in ALL_MANAGERS:
            logger.warning(f"invalid context history manager: [{mgr}]")
            continue
        args=[]
        kwargs = {}
        for param in mgr_list[1:]:
            param_kv = param.split('=', 1)
            if len(param_kv) == 2:
                kwargs[param_kv[0]] = param_kv[1]
            else:
                args.append(param)
        if not args and not kwargs:
            logger.warning(f"missing parameters for this manager: [{mgr}]")
            continue
        mgrs.append(
            ALL_MANAGERS[mgr_name](*args, **kwargs)
        )
    # end for
    if mgrs:
        logger.info(f"got CONTEXT_HISTORY_MANAGERS: count={len(mgrs)}")
    return mgrs

def get_session_manager(conn="sqlite:///memory.db") -> SessionStorageBase:
    """ get a object of session manager """
    mgr = SessionSQLAlchemy(conn)
    return mgr

def get_messages_by_session(session_id:str="", session_mgr:SessionStorageBase=None) -> list[dict]:
    """ retrieve messages.
    if session_id is null, trying to get it from env.
    """
    if not session_id:
        session_id = os.getenv("SESSION_ID")

    if not session_id:
        return []

    if session_mgr is None:
        session_mgr = get_session_manager()
    if session_mgr.exists_session(session_id):
        messages_from_session = session_mgr.retrieve_messages(session_id)
        logger.info(f"retrieve messages: session_id={session_id}, count={len(messages_from_session)}")
        return messages_from_session

    return []

def create_session(session_id:str, task:str, session_mgr:SessionStorageBase=None) -> bool:
    """ record a new session for the task """
    if not session_id:
        return False
    if not task:
        return False

    if session_mgr is None:
        session_mgr = get_session_manager()

    session_mgr.create_session(
        SessionData(session_id=session_id, task=task)
    )
    return True

def add_session_message(session_id:str, message:str) -> bool:
    """ add message to a session """
    history_mgrs = get_managers_by_env()
    if not history_mgrs:
        return False

    for mgr in history_mgrs:
        mgr.add_session_message(message, session_id=session_id)

    return True
