"""
microsoft_bond_collections.py
Copyright: Microsoft 2016
"""

class Set:
    """Set implementation for Bond"""
    def __init__(self):
        self._buffer = []

    def add(self, item):
        if item not in self._buffer:
            self._buffer.append(item)

    def count(self):
        return len(self._buffer)

    def get_buffer(self):
        return self._buffer
