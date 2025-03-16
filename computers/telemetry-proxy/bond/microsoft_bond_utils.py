"""
microsoft_bond_utils.py
Copyright: Microsoft 2016
"""

import importlib

class BrowserChecker:
    @staticmethod
    def is_data_view_support():
        """Check if DataView is supported in the current environment"""
        try:
            return importlib.util.find_spec("array") and importlib.util.find_spec("struct")
        except ImportError:
            return False


class EnvironmentChecker:
    @staticmethod
    def is_binary_support():
        """Check if binary operations are supported in the current environment"""
        try:
            return importlib.util.find_spec("array") and importlib.util.find_spec("struct")
        except ImportError:
            return False
