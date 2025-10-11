package com.facility.client.common;

import java.nio.ByteBuffer;
import java.nio.charset.StandardCharsets;

public class ByteBufferWrapper {
    private ByteBuffer buffer;
    
    public ByteBufferWrapper() {
        this.buffer = ByteBuffer.allocate(MessageTypes.MAX_BUFFER_SIZE);
    }
    
    public ByteBufferWrapper(byte[] data) {
        this.buffer = ByteBuffer.wrap(data);
    }
    
    // Write operations
    public void writeUInt8(int val) {
        buffer.put((byte) (val & 0xFF));
    }
    
    public void writeUInt16(int val) {
        buffer.put((byte) ((val >> 8) & 0xFF));
        buffer.put((byte) (val & 0xFF));
    }
    
    public void writeUInt32(long val) {
        buffer.put((byte) ((val >> 24) & 0xFF));
        buffer.put((byte) ((val >> 16) & 0xFF));
        buffer.put((byte) ((val >> 8) & 0xFF));
        buffer.put((byte) (val & 0xFF));
    }
    
    public void writeString(String str) {
        byte[] bytes = str.getBytes(StandardCharsets.UTF_8);
        writeUInt16(bytes.length);
        buffer.put(bytes);
    }
    
    // Read operations
    public int readUInt8() {
        return buffer.get() & 0xFF;
    }
    
    public int readUInt16() {
        return ((buffer.get() & 0xFF) << 8) | (buffer.get() & 0xFF);
    }
    
    public long readUInt32() {
        return ((buffer.get() & 0xFFL) << 24) |
               ((buffer.get() & 0xFFL) << 16) |
               ((buffer.get() & 0xFFL) << 8) |
               (buffer.get() & 0xFFL);
    }
    
    public String readString() {
        int length = readUInt16();
        byte[] bytes = new byte[length];
        buffer.get(bytes);
        return new String(bytes, StandardCharsets.UTF_8);
    }
    
    // Utility methods
    public byte[] getData() {
        buffer.flip();
        byte[] data = new byte[buffer.remaining()];
        buffer.get(data);
        return data;
    }
    
    public void clear() {
        buffer.clear();
    }
}