#include "byte_buffer.h"
#include <string.h>

ByteBuffer* byte_buffer_create(void) {
    ByteBuffer* bb = (ByteBuffer*)malloc(sizeof(ByteBuffer));
    if (bb) {
        bb->buffer = (uint8_t*)malloc(MAX_BUFFER_SIZE);
        bb->capacity = MAX_BUFFER_SIZE;
        bb->size = 0;
        bb->read_pos = 0;
    }
    return bb;
}

void byte_buffer_destroy(ByteBuffer* bb) {
    if (bb) {
        free(bb->buffer);
        free(bb);
    }
}

void byte_buffer_clear(ByteBuffer* bb) {
    bb->size = 0;
    bb->read_pos = 0;
}

void byte_buffer_write_uint8(ByteBuffer* bb, uint8_t val) {
    if (bb->size < bb->capacity) {
        bb->buffer[bb->size++] = val;
    }
}

void byte_buffer_write_uint16(ByteBuffer* bb, uint16_t val) {
    byte_buffer_write_uint8(bb, (val >> 8) & 0xFF);
    byte_buffer_write_uint8(bb, val & 0xFF);
}

void byte_buffer_write_uint32(ByteBuffer* bb, uint32_t val) {
    byte_buffer_write_uint8(bb, (val >> 24) & 0xFF);
    byte_buffer_write_uint8(bb, (val >> 16) & 0xFF);
    byte_buffer_write_uint8(bb, (val >> 8) & 0xFF);
    byte_buffer_write_uint8(bb, val & 0xFF);
}

void byte_buffer_write_string(ByteBuffer* bb, const char* str) {
    size_t len = strlen(str);
    byte_buffer_write_uint16(bb, len);
    for (size_t i = 0; i < len && bb->size < bb->capacity; i++) {
        bb->buffer[bb->size++] = str[i];
    }
}

uint8_t byte_buffer_read_uint8(ByteBuffer* bb) {
    if (bb->read_pos < bb->size) {
        return bb->buffer[bb->read_pos++];
    }
    return 0;
}

uint16_t byte_buffer_read_uint16(ByteBuffer* bb) {
    uint16_t val = byte_buffer_read_uint8(bb) << 8;
    val |= byte_buffer_read_uint8(bb);
    return val;
}

uint32_t byte_buffer_read_uint32(ByteBuffer* bb) {
    uint32_t val = byte_buffer_read_uint8(bb) << 24;
    val |= byte_buffer_read_uint8(bb) << 16;
    val |= byte_buffer_read_uint8(bb) << 8;
    val |= byte_buffer_read_uint8(bb);
    return val;
}

char* byte_buffer_read_string(ByteBuffer* bb) {
    uint16_t len = byte_buffer_read_uint16(bb);
    char* str = (char*)malloc(len + 1);
    if (str) {
        for (uint16_t i = 0; i < len; i++) {
            str[i] = byte_buffer_read_uint8(bb);
        }
        str[len] = '\0';
    }
    return str;
}

const uint8_t* byte_buffer_get_data(ByteBuffer* bb) {
    return bb->buffer;
}

size_t byte_buffer_get_size(ByteBuffer* bb) {
    return bb->size;
}