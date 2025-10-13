/**
 * Byte Buffer Implementation
 */

#include "../include/byte_buffer.h"

ByteBuffer::ByteBuffer() : read_pos(0) {}

ByteBuffer::ByteBuffer(const uint8_t *data, size_t len)
    : buffer(data, data + len), read_pos(0) {}

// Write operations
void ByteBuffer::write_uint8(uint8_t val)
{
    buffer.push_back(val);
}

void ByteBuffer::write_uint16(uint16_t val)
{
    uint16_t net_val = htons(val);
    uint8_t *bytes = reinterpret_cast<uint8_t *>(&net_val);
    buffer.insert(buffer.end(), bytes, bytes + sizeof(net_val));
}

void ByteBuffer::write_uint32(uint32_t val)
{
    uint32_t net_val = htonl(val);
    uint8_t *bytes = reinterpret_cast<uint8_t *>(&net_val);
    buffer.insert(buffer.end(), bytes, bytes + sizeof(net_val));
}

void ByteBuffer::write_time(time_t val)
{
    write_uint32(static_cast<uint32_t>(val));
}

void ByteBuffer::write_string(const std::string &str)
{
    write_uint16(static_cast<uint16_t>(str.length()));
    buffer.insert(buffer.end(), str.begin(), str.end());
}

void ByteBuffer::write_bytes(const uint8_t *data, size_t len)
{
    buffer.insert(buffer.end(), data, data + len);
}

// Read operations
uint8_t ByteBuffer::read_uint8()
{
    if (read_pos >= buffer.size())
        throw std::runtime_error("Buffer underflow");
    return buffer[read_pos++];
}

uint16_t ByteBuffer::read_uint16()
{
    if (read_pos + 2 > buffer.size())
        throw std::runtime_error("Buffer underflow");
    uint16_t net_val;
    std::memcpy(&net_val, &buffer[read_pos], sizeof(net_val));
    read_pos += 2;
    return ntohs(net_val);
}

uint32_t ByteBuffer::read_uint32()
{
    if (read_pos + 4 > buffer.size())
        throw std::runtime_error("Buffer underflow");
    uint32_t net_val;
    std::memcpy(&net_val, &buffer[read_pos], sizeof(net_val));
    read_pos += 4;
    return ntohl(net_val);
}

time_t ByteBuffer::read_time()
{
    return static_cast<time_t>(read_uint32());
}

std::string ByteBuffer::read_string()
{
    uint16_t len = read_uint16();
    if (read_pos + len > buffer.size())
        throw std::runtime_error("Buffer underflow");
    std::string str(buffer.begin() + read_pos, buffer.begin() + read_pos + len);
    read_pos += len;
    return str;
}

// Utility functions
const uint8_t *ByteBuffer::data() const
{
    return buffer.data();
}

size_t ByteBuffer::size() const
{
    return buffer.size();
}

size_t ByteBuffer::remaining() const
{
    return buffer.size() - read_pos;
}

size_t ByteBuffer::position() const
{
    return read_pos;
}

void ByteBuffer::set_position(size_t pos)
{
    if (pos > buffer.size())
        throw std::runtime_error("Invalid position");
    read_pos = pos;
}
