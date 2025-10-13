package com.facility.common;

import java.io.ByteArrayOutputStream;
import java.nio.charset.StandardCharsets;

/**
 * Byte Buffer for Marshalling and Unmarshalling
 */
public class ByteBuffer {
    private ByteArrayOutputStream buffer;
    private byte[] readBuffer;
    private int readPos;

    public ByteBuffer() {
        this.buffer = new ByteArrayOutputStream();
        this.readBuffer = new byte[0];
        this.readPos = 0;
    }

    public ByteBuffer(byte[] data) {
        this.buffer = new ByteArrayOutputStream();
        this.readBuffer = data;
        this.readPos = 0;
    }

    // Write operations
    public void writeUInt8(int val) {
        buffer.write(val & 0xFF);
    }

    public void writeUInt16(int val) {
        buffer.write((val >> 8) & 0xFF);
        buffer.write(val & 0xFF);
    }

    public void writeUInt32(long val) {
        buffer.write((int)((val >> 24) & 0xFF));
        buffer.write((int)((val >> 16) & 0xFF));
        buffer.write((int)((val >> 8) & 0xFF));
        buffer.write((int)(val & 0xFF));
    }

    public void writeTime(long val) {
        writeUInt32(val);
    }

    public void writeString(String s) {
        byte[] encoded = s.getBytes(StandardCharsets.UTF_8);
        writeUInt16(encoded.length);
        buffer.write(encoded, 0, encoded.length);
    }

    // Read operations
    public int readUInt8() {
        if (readPos >= readBuffer.length) {
            throw new RuntimeException("Buffer underflow");
        }
        return readBuffer[readPos++] & 0xFF;
    }

    public int readUInt16() {
        if (readPos + 2 > readBuffer.length) {
            throw new RuntimeException("Buffer underflow");
        }
        int val = ((readBuffer[readPos] & 0xFF) << 8) |
                  (readBuffer[readPos + 1] & 0xFF);
        readPos += 2;
        return val;
    }

    public long readUInt32() {
        if (readPos + 4 > readBuffer.length) {
            throw new RuntimeException("Buffer underflow");
        }
        long val = ((long)(readBuffer[readPos] & 0xFF) << 24) |
                   ((long)(readBuffer[readPos + 1] & 0xFF) << 16) |
                   ((long)(readBuffer[readPos + 2] & 0xFF) << 8) |
                   ((long)(readBuffer[readPos + 3] & 0xFF));
        readPos += 4;
        return val;
    }

    public long readTime() {
        return readUInt32();
    }

    public String readString() {
        int length = readUInt16();
        if (readPos + length > readBuffer.length) {
            throw new RuntimeException("Buffer underflow");
        }
        String s = new String(readBuffer, readPos, length, StandardCharsets.UTF_8);
        readPos += length;
        return s;
    }

    public byte[] getData() {
        return buffer.toByteArray();
    }

    public int remaining() {
        return readBuffer.length - readPos;
    }

    public int size() {
        return buffer.size();
    }

    public void write(byte[] data) {
        buffer.write(data, 0, data.length);
    }
}
