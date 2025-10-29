'''
  Author: DawsonLin
  Email: lin_dongsen@126.com
  Created: 2025-10-29
  Purpose:
'''

import os

from logger import logger

from .chat_history_manager import ALL_MANAGERS

def get_managers_by_env():
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
    return mgrs
