"""
microsoft_bond_io.py
Copyright: Microsoft 2016
"""
from .microsoft_bond_primitives import Number

class Stream:
    """Interface for a stream that can be written to"""
    def write_byte(self, byte):
        """
        Writes a byte to the current position in the stream and advances
        the position within the stream by one byte.
        """
        raise NotImplementedError()

    def write(self, buffer, offset, count):
        """
        When overridden in a derived class, writes a sequence of bytes
        to the current system and advances the current position within
        this stream by the number of bytes written.

        Args:
            buffer: An array of bytes. This method copies count bytes
                from buffer to the current stream.
            offset: The zero-based byte offset in buffer at which to
                begin copying bytes to the current stream.
            count: The number of bytes to be written to the current stream.
        """
        raise NotImplementedError()


class MemoryStream(Stream):
    """A stream that writes to memory"""
    def __init__(self):
        self._buffer = []

    def write_byte(self, byte):
        self._buffer.append(Number.to_byte(byte))

    def write(self, buffer, offset, count):
        while count > 0:
            self.write_byte(buffer[offset])
            offset += 1
            count -= 1

    def get_buffer(self):
        """Returns the array of unsigned bytes from which this stream was created."""
        return self._buffer
