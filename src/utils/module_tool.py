'''
  Author: DawsonLin
  Email: lin_dongsen@126.com
  Created: 2025-10-18
  Purpose: Module introspection and dynamic import utilities
'''

import pkgutil

def get_mod(path):
    """Dynamically import a module by its path.
    
    Args:
        path: Module path as string, e.g. 'base.internal_handlers'
    
    Returns:
        module: Imported module object
    """
    return __import__(path, None, None, [path.split('.')[-1]])

def get_var(path:str, name):
    """Get a variable from a module by path and name.
    
    Args:
        path: Module path or full path including variable name
        name: Variable name (optional if included in path)
    
    Returns:
        object: The variable value, or None if not found
    
    Note:
        If name is not provided, it will be extracted from the path
    """
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
    """List all non-package submodule names in a package.
    
    Args:
        path: Package path, e.g. 'base.internal_handlers'
    
    Returns:
        list: List of submodule names, or None if package not found
    
    Note:
        Only returns modules that are not packages and don't start with '__'
    """
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
    """Create a mapping of function names to functions from modules.
    
    This function scans modules in a package and collects functions
    stored in a specific variable (typically used for tool registration).
    
    Args:
        path: Package path to search for modules
        key: Variable name to look for in each module (default: "TOOLS")
        prefix_name: Prefix for function names in the map
            - If None: uses 'path' as prefix
            - If "": uses module name as prefix
            - Otherwise: uses the specified prefix
    
    Returns:
        dict: Mapping of function names (with prefixes) to function objects
    
    Example:
        {
            "cmd_tool.exec_cmd": exec_cmd_function
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
