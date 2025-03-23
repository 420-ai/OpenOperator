from functions import FUNCTIONS

class FunctionExecutor:
    def __init__(self, function_registry=None):
        self.function_registry = function_registry or FUNCTIONS

    def execute_from_list(self, function_list: list):
        """
        Execute functions from a list of config items.
        Each item should be a dict with 'func' and optionally 'args'.
        """
        for item in function_list:
            self.execute(item)

    def execute(self, item: dict):
        func_name = item.get("func")
        args = item.get("args", {})

        if not func_name:
            print("Warning: Missing 'func' name in item.")
            return

        func = self.function_registry.get(func_name)
        if not func:
            print(f"Warning: Function '{func_name}' not found in registry.")
            return

        try:
            if args:
                func(**args)
            else:
                func()
        except Exception as e:
            print(f"Error executing function '{func_name}': {e}")
