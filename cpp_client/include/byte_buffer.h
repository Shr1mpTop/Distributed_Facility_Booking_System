/**
 * Byte Buffer - Marshalling and Unmarshalling Utility
 * Handles conversion between data types and byte arrays
 */

#ifndef CPP_CLIENT_BYTE_BUFFER_H
#define CPP_CLIENT_BYTE_BUFFER_H

#include <vector>
#include <string>
#include <cstdint>
#include <cstring>
#include <stdexcept>
#include <arpa/inet.h>

class ByteBuffer
{
private:
    std::vector<uint8_t> buffer;
    size_t read_pos;

public:
    ByteBuffer();
    ByteBuffer(const uint8_t *data, size_t len);

    // Write operations
    void write_uint8(uint8_t val);
    void write_uint16(uint16_t val);
    void write_uint32(uint32_t val);
    void write_time(time_t val);
    void write_string(const std::string &str);
    void write_bytes(const uint8_t *data, size_t len);

    // Read operations
    uint8_t read_uint8();
    uint16_t read_uint16();
    uint32_t read_uint32();
    time_t read_time();
    std::string read_string();

    // Utility functions
    const uint8_t *data() const;
    size_t size() const;
    size_t remaining() const;
};

#endif // CPP_CLIENT_BYTE_BUFFER_H
