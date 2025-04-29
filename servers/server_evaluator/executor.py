class FunctionExecutor:
    def __init__(self, function_registry=None):
        self.function_registry = function_registry or {}

    def execute(self, item: dict, **kwargs):
        func_name = item.get("func")
        args = item.get("args", {})

        func = self.function_registry.get(func_name)
        if not func:
            raise ValueError(f"Function '{func_name}' not found in registry.")

        all_args = {**args, **kwargs}
        return func(**all_args)