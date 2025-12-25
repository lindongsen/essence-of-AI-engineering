'''
  Author: DawsonLin
  Email: lin_dongsen@126.com
  Created: 2025-12-25
  Purpose:
'''

TRIGGER_CHARS = "/@"


class HookFunc(object):
    def __init__(self, description, func, args=None, kwargs=None):
        self.description = description
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def __call__(self, *args, **kwargs):
        if not args:
            args = self.args or tuple()
        if not kwargs:
            kwargs = self.kwargs or dict()
        return self.func(*args, **kwargs)

class HookInstruction(object):
    """
    Example:
        hook_instruction = HookInstruction()
        def _clear():
            ...
        def _story():
            ...
        hook_instruction.add_hook("/clear", _clear)
        hook_instruction.add_hook("/story", _story)
        ...
        if hook_instruction.exist_hook(message):
            hook_instruction.call_hook(message)
    """
    def __init__(self):
        # key is hook_name, value is list[dict]
        # value.dict:
        #    func: func()
        #    description: ""
        self.hook_map = {
            "/help": [HookFunc("show help info", self.show_help)]
        }

    def show_help(self):
        print("Instructions:")
        for hook_name, hook_set in self.hook_map.items():
            print(f"\n  {hook_name}")
            for hook_func in hook_set:
                print(f"    - {hook_func.func.__name__}, {hook_func.description}")
        print()
        return

    def add_hook(self, hook_name, hook_func:HookFunc, description=""):
        assert callable(hook_func)
        if hook_name not in self.hook_map:
            self.hook_map[hook_name] = []

        if not isinstance(hook_func, HookFunc):
            hook_func = HookFunc(
                description=description,
                func=hook_func,
            )

        self.hook_map[hook_name].append(hook_func)
        return

    def del_hook(self, hook_name, hook_func:HookFunc):
        if hook_name in self.hook_map:
            if hook_func in self.hook_map[hook_name]:
                self.hook_map[hook_name].remove(hook_func)
        return

    def call_hook(self, hook_name):
        if hook_name not in self.hook_map:
            return
        for hook_func in self.hook_map[hook_name]:
            hook_func()
        return

    def exist_hook(self, hook_name) -> bool:
        if hook_name[0] in TRIGGER_CHARS:
            if hook_name in self.hook_map:
                return True
        return False
