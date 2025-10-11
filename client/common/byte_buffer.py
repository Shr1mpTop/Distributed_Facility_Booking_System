"""
Byte Buffer for Marshalling and Unmarshalling
"""

import struct


class ByteBuffer:
    """Helper class for marshalling and unmarshalling data."""
    
    def __init__(self, data: bytes = b''):
        self.buffer = bytearray(data)
        self.read_pos = 0
    
    # Write operations
    def write_uint8(self, val: int):
        """Write an 8-bit unsigned integer."""
        self.buffer.append(val & 0xFF)
    
    def write_uint16(self, val: int):
        """Write a 16-bit unsigned integer in network byte order."""
        self.buffer.extend(struct.pack('!H', val))
    
    def write_uint32(self, val: int):
        """Write a 32-bit unsigned integer in network byte order."""
        self.buffer.extend(struct.pack('!I', val))
    
    def write_time(self, val: int):
        """Write a time_t value (as 32-bit unsigned int)."""
        self.write_uint32(val)
    
    def write_string(self, s: str):
        """Write a length-prefixed string."""
        encoded = s.encode('utf-8')
        self.write_uint16(len(encoded))
        self.buffer.extend(encoded)
    
    # Read operations
    def read_uint8(self) -> int:
        """Read an 8-bit unsigned integer."""
        if self.read_pos >= len(self.buffer):
            raise ValueError("Buffer underflow")
        val = self.buffer[self.read_pos]
        self.read_pos += 1
        return val
    
    def read_uint16(self) -> int:
        """Read a 16-bit unsigned integer from network byte order."""
        if self.read_pos + 2 > len(self.buffer):
            raise ValueError("Buffer underflow")
        val = struct.unpack('!H', self.buffer[self.read_pos:self.read_pos + 2])[0]
        self.read_pos += 2
        return val
    
    def read_uint32(self) -> int:
        """Read a 32-bit unsigned integer from network byte order."""
        if self.read_pos + 4 > len(self.buffer):
            raise ValueError("Buffer underflow")
        val = struct.unpack('!I', self.buffer[self.read_pos:self.read_pos + 4])[0]
        self.read_pos += 4
        return val
    
    def read_time(self) -> int:
        """Read a time_t value (as 32-bit unsigned int)."""
        return self.read_uint32()
    
    def read_string(self) -> str:
        """Read a length-prefixed string."""
        length = self.read_uint16()
        if self.read_pos + length > len(self.buffer):
            raise ValueError("Buffer underflow")
        s = self.buffer[self.read_pos:self.read_pos + length].decode('utf-8')
        self.read_pos += length
        return s
    
    def get_data(self) -> bytes:
        """Get the complete buffer as bytes."""
        return bytes(self.buffer)
    
    def remaining(self) -> int:
        """Get the number of unread bytes."""
        return len(self.buffer) - self.read_pos
