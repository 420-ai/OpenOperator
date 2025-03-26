from functions import FUNCTIONS

class FunctionExecutor:
    def __init__(self, function_registry=None):
        self.function_registry = function_registry or FUNCTIONS

    def execute_from_list(self, function_list: list, **kwargs):
        """
        Execute functions from a list of config items.
        Each item should be a dict with 'func' and optionally 'args'.
        """
        for item in function_list:
            self.execute(item, **kwargs)

    def execute(self, item: dict, **kwargs):
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
            all_args = {**args}
            if kwargs:
                all_args.update(kwargs)

            if args:
                print(f"Executing function '{func_name}' with args: {all_args}")
                func(**all_args)
            else:
                func()
        except Exception as e:
            print(f"Error executing function '{func_name}': {e}")

if __name__ == "__main__":
    executor = FunctionExecutor({
        "example_function": lambda arg1, extra_arg: print(f"Function executed with arg1: {arg1} {extra_arg}"),
        "another_function": lambda: print("Another function executed")
    })
    # Example usage
    function_list = [
        {"func": "example_function", "args": {"arg1": "value1"}},
        {"func": "another_function"}
    ]
    executor.execute_from_list(function_list, extra_arg="extra_value")