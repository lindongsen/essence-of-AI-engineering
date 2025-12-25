'''
  Author: DawsonLin
  Email: lin_dongsen@126.com
  Created: 2025-12-25
  Purpose:
'''

TRIGGER_CHARS = "/@"

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
        # key is hook_name, value is list[func()]
        self.hook_map = {}

    def add_hook(self, hook_name, hook_func):
        assert callable(hook_func)
        if hook_name not in self.hook_map:
            self.hook_map[hook_name] = []
        self.hook_map[hook_name].append(hook_func)
        return

    def del_hook(self, hook_name, hook_func):
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
