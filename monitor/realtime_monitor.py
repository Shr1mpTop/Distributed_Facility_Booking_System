#!/usr/bin/env python3
"""
Real-time Server Response Monitor
Monitors server.log file and displays server activity in real-time
"""

import sys
import time
import re
from datetime import datetime
from pathlib import Path


class ServerMonitor:
    """Simple real-time server log monitor"""
    
    def __init__(self, log_file="server.log"):
        self.log_file = Path(log_file)
        self.message_types = {
            1: "QUERY_AVAILABILITY",
            2: "BOOK_FACILITY",
            3: "CHANGE_BOOKING",
            4: "MONITOR_FACILITY",
            5: "GET_LAST_BOOKING_TIME",
            6: "EXTEND_BOOKING",
            100: "RESPONSE_SUCCESS",
            101: "RESPONSE_ERROR",
            111: "HEARTBEAT/MONITOR"
        }
        
        # Statistics
        self.total_requests = 0
        self.total_responses = 0
        self.errors = 0
        self.start_time = time.time()
        
    def get_message_type_name(self, msg_type):
        """Get human-readable message type name"""
        return self.message_types.get(msg_type, f"UNKNOWN({msg_type})")
    
    def format_timestamp(self):
        """Get formatted current timestamp"""
        return datetime.now().strftime("%H:%M:%S")
    
    def parse_line(self, line):
        """Parse a log line and extract information"""
        # Extract thread ID if present
        thread_id = None
        thread_match = re.search(r'\[Thread (0x[0-9a-f]+)\]', line)
        if thread_match:
            thread_id = thread_match.group(1)[-6:]  # Last 6 chars
        
        # Received messages
        match = re.search(r'Received (\d+) bytes from ([\d.]+):(\d+) \(Total: (\d+)\)', line)
        if match:
            bytes_recv, ip, port, total = match.groups()
            self.total_requests = int(total)
            return {
                'type': 'RECEIVED',
                'bytes': bytes_recv,
                'client': f"{ip}:{port}",
                'total': total,
                'thread': thread_id
            }
        
        # Processing requests
        match = re.search(r'Processing request ID: (\d+), Type: (\d+)', line)
        if match:
            req_id, msg_type = match.groups()
            return {
                'type': 'PROCESSING',
                'request_id': req_id,
                'message_type': int(msg_type),
                'message_name': self.get_message_type_name(int(msg_type)),
                'thread': thread_id
            }
        
        # Sent responses
        match = re.search(r'Sent (\d+) bytes response', line)
        if match:
            self.total_responses += 1
            return {
                'type': 'SENT',
                'bytes': match.group(1),
                'thread': thread_id
            }
        
        # Errors
        if 'Error:' in line:
            self.errors += 1
            match = re.search(r'Error: (.+)$', line)
            if match:
                return {
                    'type': 'ERROR',
                    'message': match.group(1).strip()
                }
        
        # Operation messages
        for operation in ['Book facility:', 'Query availability for', 'Change booking:', 
                         'Monitor facility:', 'Extend booking:', 'Get last booking time for:']:
            if operation in line:
                match = re.search(f'{operation}\\s*(.+)$', line)
                if match:
                    return {
                        'type': 'OPERATION',
                        'operation': operation.rstrip(':'),
                        'target': match.group(1).strip()
                    }
        
        # Booking created
        match = re.search(r'Created booking ID: (\d+)', line)
        if match:
            return {
                'type': 'BOOKING_CREATED',
                'booking_id': match.group(1)
            }
        
        return None
    
    def display_event(self, event):
        """Display a parsed event"""
        timestamp = self.format_timestamp()
        thread = f"[T:{event.get('thread', '------')}] " if event.get('thread') else ""
        
        if event['type'] == 'RECEIVED':
            print(f"[{timestamp}] RECEIVED: {event['bytes']} bytes from {event['client']}")
        
        elif event['type'] == 'PROCESSING':
            print(f"[{timestamp}] {thread}PROCESSING: {event['message_name']} (ID: {event['request_id']})")
        
        elif event['type'] == 'SENT':
            print(f"[{timestamp}] {thread}SENT: {event['bytes']} bytes")
        
        elif event['type'] == 'ERROR':
            print(f"[{timestamp}] {thread}ERROR: {event['message']}")
        
        elif event['type'] == 'OPERATION':
            print(f"[{timestamp}] {thread}{event['operation']}: {event['target']}")
        
        elif event['type'] == 'BOOKING_CREATED':
            print(f"[{timestamp}] {thread}Booking created: ID {event['booking_id']}")
    
    def display_stats(self):
        """Display statistics"""
        runtime = time.time() - self.start_time
        print("\n" + "="*60)
        print(f"📊 STATISTICS (Runtime: {runtime:.1f}s)")
        print(f"   Total Requests: {self.total_requests}")
        print(f"   Total Responses: {self.total_responses}")
        print(f"   Errors: {self.errors}")
        if runtime > 0:
            print(f"   Requests/sec: {self.total_requests/runtime:.2f}")
        print("="*60 + "\n")
    
    def tail_log(self):
        """Monitor log file in real-time (like tail -f)"""
        if not self.log_file.exists():
            print(f"❌ Log file not found: {self.log_file}")
            print(f"   Please start the server first to generate {self.log_file}")
            return
        
        print("="*60)
        print("🔍 Real-time Server Monitor")
        print(f"   Monitoring: {self.log_file}")
        print(f"   Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        print("Press Ctrl+C to stop\n")
        
        try:
            with open(self.log_file, 'r') as f:
                # Move to end of file
                f.seek(0, 2)
                
                while True:
                    line = f.readline()
                    if line:
                        event = self.parse_line(line)
                        if event:
                            self.display_event(event)
                    else:
                        time.sleep(0.1)
        
        except KeyboardInterrupt:
            print("\n\n🛑 Monitor stopped")
            self.display_stats()
        except Exception as e:
            print(f"\n❌ Error: {e}")
    
    def analyze_existing_log(self):
        """Analyze existing log file"""
        if not self.log_file.exists():
            print(f"❌ Log file not found: {self.log_file}")
            return
        
        print("="*60)
        print("📋 Analyzing Existing Log")
        print(f"   File: {self.log_file}")
        print("="*60 + "\n")
        
        with open(self.log_file, 'r') as f:
            for line in f:
                event = self.parse_line(line)
                if event:
                    self.display_event(event)
        
        self.display_stats()


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python realtime_monitor.py tail [logfile]    # Real-time monitoring (default)")
        print("  python realtime_monitor.py analyze [logfile] # Analyze existing log")
        print("\nDefault logfile: server.log")
        sys.exit(1)
    
    mode = sys.argv[1]
    log_file = sys.argv[2] if len(sys.argv) > 2 else "server.log"
    
    monitor = ServerMonitor(log_file)
    
    if mode == "tail":
        monitor.tail_log()
    elif mode == "analyze":
        monitor.analyze_existing_log()
    else:
        print(f"❌ Unknown mode: {mode}")
        print("   Use 'tail' or 'analyze'")
        sys.exit(1)


if __name__ == "__main__":
    main()
