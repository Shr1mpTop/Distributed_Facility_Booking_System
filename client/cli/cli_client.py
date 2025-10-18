#!/usr/bin/env python3
"""
Distributed Facility Booking System - Python Client

This client communicates with the C++ server via UDP to manage facility bookings.
It provides a text-based console interface for users.

Usage: python3 client.py <server_ip> <server_port>
"""

import socket
import struct
import sys
import time
from typing import List, Tuple, Optional
from datetime import datetime, timedelta

# Message type constants (must match server)
MSG_QUERY_AVAILABILITY = 1
MSG_BOOK_FACILITY = 2
MSG_CHANGE_BOOKING = 3
MSG_MONITOR_FACILITY = 4
MSG_GET_LAST_BOOKING_TIME = 5
MSG_EXTEND_BOOKING = 6
MSG_RESPONSE_SUCCESS = 100
MSG_RESPONSE_ERROR = 101

# Booking operation types (for monitor notifications)
OP_BOOK = 1
OP_CHANGE = 2
OP_EXTEND = 3

# Network constants
TIMEOUT_SECONDS = 3
MAX_RETRIES = 3
MAX_BUFFER_SIZE = 65507


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


class FacilityBookingClient:
    """Client for the distributed facility booking system."""
    
    def __init__(self, server_ip: str, server_port: int, drop_rate: float = 0.0):
        self.server_ip = server_ip
        self.server_port = server_port
        self.drop_rate = drop_rate
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(TIMEOUT_SECONDS)
        self.next_request_id = 1
        
    def _get_next_request_id(self) -> int:
        """Get the next request ID and increment counter."""
        request_id = self.next_request_id
        self.next_request_id += 1
        return request_id
    
    def _send_request(self, request_data: bytes, retries: int = MAX_RETRIES) -> Optional[bytes]:
        """
        Send a request to the server and wait for a response.
        Implements retry logic for at-least-once semantics.
        """
        import random
        
        for attempt in range(retries):
            try:
                # Simulate packet drop on client side by not sending
                if random.random() < self.drop_rate:
                    print(f"[DROP] Request packet dropped (attempt {attempt + 1}/{retries})")
                    # Fall through to timeout
                else:
                    # Send request
                    self.sock.sendto(request_data, (self.server_ip, self.server_port))
                
                # Wait for response
                response_data, _ = self.sock.recvfrom(MAX_BUFFER_SIZE)
                return response_data
                
            except socket.timeout:
                print(f"Timeout, retransmitting... (attempt {attempt + 2}/{retries})")
                if attempt >= retries - 1:
                    print("Request timeout after all retries")
                    return None
        
        return None
    
    def query_availability(self):
        """Query facility availability for specific days."""
        print("\n=== Query Facility Availability ===")
        
        facility_name = input("Enter facility name: ").strip()
        days_input = input("Enter days to check (comma-separated, 0=today, 1=tomorrow, etc.): ").strip()
        
        try:
            days = [int(d.strip()) for d in days_input.split(',')]
        except ValueError:
            print("Invalid days format")
            return
        
        # Build request
        request = ByteBuffer()
        request_id = self._get_next_request_id()
        request.write_uint32(request_id)
        request.write_uint8(MSG_QUERY_AVAILABILITY)
        
        # Build payload first to calculate length
        payload = ByteBuffer()
        payload.write_string(facility_name)
        payload.write_uint16(len(days))
        for day in days:
            payload.write_uint32(day)
        
        request.write_uint16(len(payload.buffer))
        request.buffer.extend(payload.buffer)
        
        # Send request
        response_data = self._send_request(request.get_data())
        if not response_data:
            return
        
        # Parse response
        response = ByteBuffer(response_data)
        resp_request_id = response.read_uint32()
        status = response.read_uint8()
        
        if status == MSG_RESPONSE_ERROR:
            error_msg = response.read_string()
            print(f"Error: {error_msg}")
            return
        
        # Read available time slots
        num_slots = response.read_uint16()
        print(f"\n{num_slots} available time slots found:")
        
        for i in range(num_slots):
            start_time = response.read_time()
            end_time = response.read_time()
            
            start_dt = datetime.fromtimestamp(start_time)
            end_dt = datetime.fromtimestamp(end_time)
            
            print(f"  {i+1}. {start_dt.strftime('%Y-%m-%d %H:%M')} to {end_dt.strftime('%H:%M')}")
    
    def book_facility(self):
        """Book a facility for a specific time slot."""
        print("\n=== Book Facility ===")
        
        facility_name = input("Enter facility name: ").strip()
        
        print("Enter start time:")
        date_str = input("  Date (YYYY-MM-DD): ").strip()
        time_str = input("  Time (HH:MM): ").strip()
        
        try:
            start_dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
            start_time = int(start_dt.timestamp())
        except ValueError:
            print("Invalid date/time format")
            return
        
        duration_hours = input("Duration in hours: ").strip()
        try:
            duration_hours = float(duration_hours)
            end_time = start_time + int(duration_hours * 3600)
        except ValueError:
            print("Invalid duration")
            return
        
        # Build request
        request = ByteBuffer()
        request_id = self._get_next_request_id()
        request.write_uint32(request_id)
        request.write_uint8(MSG_BOOK_FACILITY)
        
        payload = ByteBuffer()
        payload.write_string(facility_name)
        payload.write_time(start_time)
        payload.write_time(end_time)
        
        request.write_uint16(len(payload.buffer))
        request.buffer.extend(payload.buffer)
        
        # Send request
        response_data = self._send_request(request.get_data())
        if not response_data:
            return
        
        # Parse response
        response = ByteBuffer(response_data)
        resp_request_id = response.read_uint32()
        status = response.read_uint8()
        
        if status == MSG_RESPONSE_ERROR:
            error_msg = response.read_string()
            print(f"Error: {error_msg}")
            return
        
        # Read confirmation ID
        confirmation_id = response.read_uint32()
        print(f"\n✓ Booking successful!")
        print(f"  Confirmation ID: {confirmation_id}")
        print(f"  Facility: {facility_name}")
        print(f"  Time: {datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M')} to {datetime.fromtimestamp(end_time).strftime('%H:%M')}")
    
    def change_booking(self):
        """Change an existing booking by offsetting the time."""
        print("\n=== Change Booking ===")
        
        try:
            confirmation_id = int(input("Enter confirmation ID: ").strip())
            offset_minutes = int(input("Enter time offset in minutes (positive or negative): ").strip())
        except ValueError:
            print("Invalid input")
            return
        
        # Build request
        request = ByteBuffer()
        request_id = self._get_next_request_id()
        request.write_uint32(request_id)
        request.write_uint8(MSG_CHANGE_BOOKING)
        
        payload = ByteBuffer()
        payload.write_uint32(confirmation_id)
        payload.write_uint32(offset_minutes & 0xFFFFFFFF)  # Handle negative as unsigned
        
        request.write_uint16(len(payload.buffer))
        request.buffer.extend(payload.buffer)
        
        # Send request
        response_data = self._send_request(request.get_data())
        if not response_data:
            return
        
        # Parse response
        response = ByteBuffer(response_data)
        resp_request_id = response.read_uint32()
        status = response.read_uint8()
        
        if status == MSG_RESPONSE_ERROR:
            error_msg = response.read_string()
            print(f"Error: {error_msg}")
            return
        
        message = response.read_string()
        print(f"\n✓ {message}")
    
    def monitor_facility(self):
        """Monitor a facility for updates."""
        print("\n=== Monitor Facility ===")
        
        facility_name = input("Enter facility name to monitor: ").strip()
        
        try:
            duration_seconds = int(input("Enter monitoring duration in seconds: ").strip())
        except ValueError:
            print("Invalid duration")
            return
        
        # Build request
        request = ByteBuffer()
        request_id = self._get_next_request_id()
        request.write_uint32(request_id)
        request.write_uint8(MSG_MONITOR_FACILITY)
        
        payload = ByteBuffer()
        payload.write_string(facility_name)
        payload.write_uint32(duration_seconds)
        
        request.write_uint16(len(payload.buffer))
        request.buffer.extend(payload.buffer)
        
        # Send request
        response_data = self._send_request(request.get_data())
        if not response_data:
            return
        
        # Parse response
        response = ByteBuffer(response_data)
        resp_request_id = response.read_uint32()
        status = response.read_uint8()
        
        if status == MSG_RESPONSE_ERROR:
            error_msg = response.read_string()
            print(f"Error: {error_msg}")
            return
        
        message = response.read_string()
        print(f"\n✓ {message}")
        print(f"Monitoring for {duration_seconds} seconds...")
        print("(Waiting for updates from server...)")
        print("Note: During monitoring, you cannot input new requests.\n")
        
        # Listen for updates
        start_time_monitor = time.time()
        self.sock.settimeout(1.0)  # Short timeout for checking elapsed time
        update_count = 0
        consecutive_timeouts = 0  # Track consecutive timeouts to detect connection issues
        processed_updates = set()  # Track processed updates to avoid duplicates
        
        try:
            while time.time() - start_time_monitor < duration_seconds:
                try:
                    update_data, _ = self.sock.recvfrom(MAX_BUFFER_SIZE)
                    
                    # Parse update (server-initiated messages have request_id = 0)
                    update = ByteBuffer(update_data)
                    update_request_id = update.read_uint32()
                    update_status = update.read_uint8()
                    
                    if update_status == MSG_RESPONSE_SUCCESS:
                        update_msg = update.read_string()
                        operation = update.read_uint8()
                        booking_id = update.read_uint32()
                        start_time_slot = update.read_time()
                        end_time_slot = update.read_time()
                        
                        # Check for duplicate updates
                        update_key = (booking_id, operation, start_time_slot, end_time_slot)
                        if update_key in processed_updates:
                            continue  # Skip duplicate update
                        processed_updates.add(update_key)
                        
                        update_count += 1
                        current_time = datetime.now().strftime('%H:%M:%S')
                        print(f"\n{'='*60}")
                        print(f"[{current_time}] UPDATE #{update_count}: {update_msg}")
                        print(f"{'='*60}")
                        print(f"  Booking ID: {booking_id}")
                        
                        start_dt = datetime.fromtimestamp(start_time_slot)
                        end_dt = datetime.fromtimestamp(end_time_slot)
                        print(f"  Time Slot:  {start_dt.strftime('%Y-%m-%d %H:%M')} to {end_dt.strftime('%H:%M')}")
                        
                        # For change/extend operations, show old times
                        if operation == 2 or operation == 3:  # OP_CHANGE or OP_EXTEND
                            old_start_time = update.read_time()
                            old_end_time = update.read_time()
                            
                            old_start_dt = datetime.fromtimestamp(old_start_time)
                            old_end_dt = datetime.fromtimestamp(old_end_time)
                            print(f"  Previous:   {old_start_dt.strftime('%Y-%m-%d %H:%M')} to {old_end_dt.strftime('%H:%M')}")
                        
                        print(f"{'='*60}\n")
                        consecutive_timeouts = 0  # Reset timeout counter on successful update
                    
                except socket.timeout:
                    consecutive_timeouts += 1
                    if consecutive_timeouts >= 10:
                        response_data = self._send_request(request.get_data())
                        if response_data:
                            # Parse response if needed, but for monitor, just continue
                            pass
                        consecutive_timeouts = 0  # Reset after resend
                    continue
                except Exception as e:
                    print(f"Error processing update: {e}")
                    import traceback
                    traceback.print_exc()
                    continue
        
        except KeyboardInterrupt:
            print("\n\nMonitoring interrupted by user")
        
        print(f"\nMonitoring period ended. Received {update_count} update(s).")
        self.sock.settimeout(TIMEOUT_SECONDS)  # Restore original timeout
    
    def get_last_booking_time(self):
        """Get the last booking time for a facility (idempotent operation)."""
        print("\n=== Get Last Booking Time ===")
        
        facility_name = input("Enter facility name: ").strip()
        
        # Build request
        request = ByteBuffer()
        request_id = self._get_next_request_id()
        request.write_uint32(request_id)
        request.write_uint8(MSG_GET_LAST_BOOKING_TIME)
        
        payload = ByteBuffer()
        payload.write_string(facility_name)
        
        request.write_uint16(len(payload.buffer))
        request.buffer.extend(payload.buffer)
        
        # Send request
        response_data = self._send_request(request.get_data())
        if not response_data:
            return
        
        # Parse response
        response = ByteBuffer(response_data)
        resp_request_id = response.read_uint32()
        status = response.read_uint8()
        
        if status == MSG_RESPONSE_ERROR:
            error_msg = response.read_string()
            print(f"Error: {error_msg}")
            return
        
        last_time = response.read_time()
        message = response.read_string()
        
        if last_time == 0:
            print(f"\n{message}")
        else:
            last_dt = datetime.fromtimestamp(last_time)
            print(f"\nLast booking end time: {last_dt.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Status: {message}")
    
    def extend_booking(self):
        """Extend an existing booking (non-idempotent operation)."""
        print("\n=== Extend Booking ===")
        
        try:
            confirmation_id = int(input("Enter confirmation ID: ").strip())
            minutes_to_extend = int(input("Enter minutes to extend: ").strip())
        except ValueError:
            print("Invalid input")
            return
        
        # Build request
        request = ByteBuffer()
        request_id = self._get_next_request_id()
        request.write_uint32(request_id)
        request.write_uint8(MSG_EXTEND_BOOKING)
        
        payload = ByteBuffer()
        payload.write_uint32(confirmation_id)
        payload.write_uint32(minutes_to_extend)
        
        request.write_uint16(len(payload.buffer))
        request.buffer.extend(payload.buffer)
        
        # Send request
        response_data = self._send_request(request.get_data())
        if not response_data:
            return
        
        # Parse response
        response = ByteBuffer(response_data)
        resp_request_id = response.read_uint32()
        status = response.read_uint8()
        
        if status == MSG_RESPONSE_ERROR:
            error_msg = response.read_string()
            print(f"Error: {error_msg}")
            return
        
        new_end_time = response.read_time()
        message = response.read_string()
        
        new_end_dt = datetime.fromtimestamp(new_end_time)
        print(f"\n✓ {message}")
        print(f"  New end time: {new_end_dt.strftime('%Y-%m-%d %H:%M:%S')}")
    
    def run(self):
        """Main client loop with menu interface."""
        print("=" * 60)
        print("  Distributed Facility Booking System - Client")
        print("=" * 60)
        print(f"Connected to server: {self.server_ip}:{self.server_port}\n")
        
        while True:
            print("\n" + "=" * 60)
            print("Menu:")
            print("  1. Query facility availability")
            print("  2. Book a facility")
            print("  3. Change a booking")
            print("  4. Monitor a facility")
            print("  5. Get last booking time (idempotent)")
            print("  6. Extend booking (non-idempotent)")
            print("  7. Exit")
            print("=" * 60)
            
            choice = input("Enter your choice (1-7): ").strip()
            
            try:
                if choice == '1':
                    self.query_availability()
                elif choice == '2':
                    self.book_facility()
                elif choice == '3':
                    self.change_booking()
                elif choice == '4':
                    self.monitor_facility()
                elif choice == '5':
                    self.get_last_booking_time()
                elif choice == '6':
                    self.extend_booking()
                elif choice == '7':
                    print("\nGoodbye!")
                    break
                else:
                    print("Invalid choice, please try again")
            except Exception as e:
                print(f"Error: {e}")
                import traceback
                traceback.print_exc()
        
        self.sock.close()


def main():
    # Default server address
    server_ip = "8.148.159.175"
    server_port = 8080
    drop_rate = 0.0
    
    # Parse command line arguments
    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg == "--drop-rate":
            if i + 1 < len(sys.argv):
                try:
                    drop_rate = float(sys.argv[i + 1])
                    if drop_rate < 0.0 or drop_rate > 1.0:
                        print("Error: drop-rate must be between 0.0 and 1.0")
                        return
                    i += 2
                except ValueError:
                    print("Error: drop-rate must be a number")
                    return
            else:
                print("Error: --drop-rate requires a value")
                return
        elif arg.startswith("--"):
            print(f"Unknown option: {arg}")
            print("Usage: python cli_client.py [server_ip] [server_port] [--drop-rate rate]")
            return
        else:
            # Positional arguments
            if i == 1:
                server_ip = arg
            elif i == 2:
                try:
                    server_port = int(arg)
                except ValueError:
                    print("Error: server_port must be a number")
                    return
            else:
                print("Too many positional arguments")
                print("Usage: python cli_client.py [server_ip] [server_port] [--drop-rate rate]")
                return
            i += 1
    
    print(f"Connecting to server: {server_ip}:{server_port}")
    if drop_rate > 0.0:
        print(f"Packet drop rate: {drop_rate}")
    
    client = FacilityBookingClient(server_ip, server_port, drop_rate)
    client.run()


if __name__ == '__main__':
    main()
