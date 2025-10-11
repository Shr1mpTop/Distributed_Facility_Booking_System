#ifndef BYTE_BUFFER_H
#define BYTE_BUFFER_H

#include <stdint.h>
#include <stdlib.h>

#define MAX_BUFFER_SIZE 65507

typedef struct {
    uint8_t* buffer;
    size_t capacity;
    size_t size;
    size_t read_pos;
} ByteBuffer;

// Initialize and cleanup
ByteBuffer* byte_buffer_create(void);
void byte_buffer_destroy(ByteBuffer* bb);
void byte_buffer_clear(ByteBuffer* bb);

// Write operations
void byte_buffer_write_uint8(ByteBuffer* bb, uint8_t val);
void byte_buffer_write_uint16(ByteBuffer* bb, uint16_t val);
void byte_buffer_write_uint32(ByteBuffer* bb, uint32_t val);
void byte_buffer_write_string(ByteBuffer* bb, const char* str);

// Read operations
uint8_t byte_buffer_read_uint8(ByteBuffer* bb);
uint16_t byte_buffer_read_uint16(ByteBuffer* bb);
uint32_t byte_buffer_read_uint32(ByteBuffer* bb);
char* byte_buffer_read_string(ByteBuffer* bb);

// Utility functions
const uint8_t* byte_buffer_get_data(ByteBuffer* bb);
size_t byte_buffer_get_size(ByteBuffer* bb);

#endif // BYTE_BUFFER_H