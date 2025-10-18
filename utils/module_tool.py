'''
  Author: DawsonLin
  Email: lin_dongsen@126.com
  Created: 2025-10-18
  Purpose:
'''

import pkgutil

def get_mod(path):
    ''' return modules.
    :path: module path, e.g 'base.internal_handlers'
    '''
    return __import__(path, None, None, [path.split('.')[-1]])

def get_var(path:str, name):
    """ return var of path.name """
    if not name:
        path, name = path.rsplit('.', 1)
    sub_mod = get_mod(path)
    var = None
    try:
        var = getattr(sub_mod, name)
    except Exception as e:
        print(f"{sub_mod}, {name}, {e}")
    return var

def list_sub_mods_name(path):
    ''' return sub mods' name
    :path: module path, e.g 'base.internal_handlers'
    '''
    mod = get_mod(path)
    if not mod:
        return None
    #
    mod_name_set = []
    for _, modname, ispkg in pkgutil.iter_modules(mod.__path__):
        if not ispkg and not modname.startswith('__'):
            mod_name_set.append(modname)
    return mod_name_set

def get_function_map(path, key="TOOLS", prefix_name=""):
    """
    # parameters
    :path: list all of modules from the path.
    :key: search variable name for the key.
    :prefix_name:
        if it is None, default use 'path' as prefix.
        if it is "", use module name as preix.

    # return dict, key is name, value is function.

    # exmaple
    {
        "cmd_tool.exec_cmd": exec_cmd
    }
    """
    if prefix_name is None:
        prefix_name = path

    modules_map = {}
    for sub_modname in list_sub_mods_name(path):
        values = get_var("%s.%s" % (path, sub_modname), key)
        if not values:
            continue

        iter_values = None
        if isinstance(values, dict):
            iter_values = values.items()
        elif isinstance(values, (list, set, tuple)):
            iter_values = enumerate(values)
        if iter_values is None:
            print(f"BUG? module={sub_mod}, values={values}")
            continue

        for v_name, v_func in iter_values:
            if not isinstance(v_name, str):
                v_name = v_func.__name__
            m_key = f"{sub_modname}.{v_name}"
            if prefix_name:
                m_key = f"{prefix_name}.{m_key}"
            modules_map[m_key] = v_func
    return modules_map
