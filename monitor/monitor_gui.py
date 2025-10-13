#!/usr/bin/env python3
"""
Simple GUI Monitor for Server Responses
Real-time visualization of server activity
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import time
import re
from pathlib import Path
from datetime import datetime
from collections import deque


class ServerMonitorGUI:
    """Simple GUI for monitoring server activity"""
    
    def __init__(self, root, log_file="server.log"):
        self.root = root
        self.log_file = Path(log_file)
        self.running = False
        self.monitor_thread = None
        
        # Statistics
        self.total_requests = 0
        self.total_responses = 0
        self.errors = 0
        self.recent_events = deque(maxlen=100)
        
        # Message type mapping
        self.message_types = {
            1: "QUERY_AVAILABILITY",
            2: "BOOK_FACILITY",
            3: "CHANGE_BOOKING",
            4: "MONITOR_FACILITY",
            5: "GET_LAST_BOOKING_TIME",
            6: "EXTEND_BOOKING",
            111: "HEARTBEAT"
        }
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the GUI interface"""
        self.root.title("Server Monitor")
        self.root.geometry("900x600")
        
        # Top frame - Statistics
        stats_frame = ttk.LabelFrame(self.root, text="Statistics", padding=10)
        stats_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Create statistics labels
        self.stats_labels = {}
        stats_info = [
            ("Requests", "total_requests"),
            ("Responses", "total_responses"),
            ("Errors", "errors"),
            ("Status", "status")
        ]
        
        for i, (label_text, key) in enumerate(stats_info):
            ttk.Label(stats_frame, text=f"{label_text}:").grid(row=0, column=i*2, padx=5, sticky=tk.W)
            label = ttk.Label(stats_frame, text="0", font=("Arial", 12, "bold"))
            label.grid(row=0, column=i*2+1, padx=5, sticky=tk.W)
            self.stats_labels[key] = label
        
        # Middle frame - Recent Activity
        activity_frame = ttk.LabelFrame(self.root, text="Recent Activity", padding=10)
        activity_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Activity text area with color tags
        self.activity_text = scrolledtext.ScrolledText(
            activity_frame,
            wrap=tk.WORD,
            font=("Courier", 10),
            bg="#1e1e1e",
            fg="#d4d4d4"
        )
        self.activity_text.pack(fill=tk.BOTH, expand=True)
        
        # Configure text tags for colors
        self.activity_text.tag_config("received", foreground="#4ec9b0")
        self.activity_text.tag_config("processing", foreground="#dcdcaa")
        self.activity_text.tag_config("sent", foreground="#569cd6")
        self.activity_text.tag_config("error", foreground="#f48771")
        self.activity_text.tag_config("success", foreground="#4fc1ff")
        self.activity_text.tag_config("timestamp", foreground="#858585")
        self.activity_text.tag_config("thread", foreground="#c586c0")
        
        # Bottom frame - Controls
        control_frame = ttk.Frame(self.root, padding=10)
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.start_button = ttk.Button(control_frame, text="Start Monitoring", command=self.toggle_monitoring)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(control_frame, text="Clear", command=self.clear_display).pack(side=tk.LEFT, padx=5)
        
        # Log file path
        ttk.Label(control_frame, text=f"Monitoring: {self.log_file}").pack(side=tk.RIGHT, padx=5)
    
    def toggle_monitoring(self):
        """Start or stop monitoring"""
        if not self.running:
            self.start_monitoring()
        else:
            self.stop_monitoring()
    
    def start_monitoring(self):
        """Start monitoring the log file"""
        if not self.log_file.exists():
            self.log_message(f"ERROR: Log file not found: {self.log_file}", "error")
            return
        
        self.running = True
        self.start_button.config(text="Stop Monitoring")
        self.update_status("Running")
        self.monitor_thread = threading.Thread(target=self.monitor_log, daemon=True)
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.running = False
        self.start_button.config(text="Start Monitoring")
        self.update_status("Stopped")
    
    def monitor_log(self):
        """Monitor log file in real-time"""
        try:
            with open(self.log_file, 'r') as f:
                # Move to end of file
                f.seek(0, 2)
                
                while self.running:
                    line = f.readline()
                    if line:
                        self.process_log_line(line)
                    else:
                        time.sleep(0.1)
        except Exception as e:
            self.log_message(f"ERROR: {e}", "error")
    
    def process_log_line(self, line):
        """Process a single log line"""
        # Extract thread ID if present
        thread_id = None
        thread_match = re.search(r'\[Thread (0x[0-9a-f]+)\]', line)
        if thread_match:
            thread_id = thread_match.group(1)[-6:]  # Last 6 chars for display
        
        thread_str = f"[T:{thread_id}] " if thread_id else ""
        
        # Received messages
        match = re.search(r'Received (\d+) bytes from ([\d.]+):(\d+) \(Total: (\d+)\)', line)
        if match:
            bytes_recv, ip, port, total = match.groups()
            self.total_requests = int(total)
            self.update_stats()
            self.log_message(f"Received {bytes_recv} bytes from {ip}:{port}", "received")
            return
        
        # Processing requests
        match = re.search(r'Processing request ID: (\d+), Type: (\d+)', line)
        if match:
            req_id, msg_type = match.groups()
            msg_name = self.message_types.get(int(msg_type), f"TYPE_{msg_type}")
            self.log_message(f"{thread_str}Processing: {msg_name} (ID: {req_id})", "processing")
            return
        
        # Sent responses
        match = re.search(r'Sent (\d+) bytes response', line)
        if match:
            self.total_responses += 1
            self.update_stats()
            self.log_message(f"{thread_str}Sent: {match.group(1)} bytes", "sent")
            return
        
        # Errors
        if 'Error:' in line:
            self.errors += 1
            self.update_stats()
            match = re.search(r'Error: (.+)$', line)
            if match:
                # Extract thread for errors too
                thread_str = ""
                thread_match = re.search(r'\[Thread (0x[0-9a-f]+)\]', line)
                if thread_match:
                    thread_id = thread_match.group(1)[-6:]
                    thread_str = f"[T:{thread_id}] "
                self.log_message(f"{thread_str}Error: {match.group(1).strip()}", "error")
            return
                   
        # Booking created
        match = re.search(r'Created booking ID: (\d+)', line)
        if match:
            # Extract thread for booking creation
            thread_str = ""
            thread_match = re.search(r'\[Thread (0x[0-9a-f]+)\]', line)
            if thread_match:
                thread_id = thread_match.group(1)[-6:]
                thread_str = f"[T:{thread_id}] "
            self.log_message(f"{thread_str}Booking created: ID {match.group(1)}", "success")
    
    def log_message(self, message, tag=None):
        """Add message to activity log with optional color tag"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        def append():
            self.activity_text.insert(tk.END, f"[{timestamp}] ", "timestamp")
            
            # Highlight thread ID if present
            if message.startswith("[T:"):
                thread_end = message.find("]")
                if thread_end != -1:
                    self.activity_text.insert(tk.END, message[:thread_end+1] + " ", "thread")
                    self.activity_text.insert(tk.END, f"{message[thread_end+2:]}\n", tag)
                else:
                    self.activity_text.insert(tk.END, f"{message}\n", tag)
            else:
                self.activity_text.insert(tk.END, f"{message}\n", tag)
            
            self.activity_text.see(tk.END)
        
        # Schedule UI update in main thread
        self.root.after(0, append)
    
    def update_stats(self):
        """Update statistics display"""
        def update():
            self.stats_labels["total_requests"].config(text=str(self.total_requests))
            self.stats_labels["total_responses"].config(text=str(self.total_responses))
            self.stats_labels["errors"].config(text=str(self.errors))
        
        self.root.after(0, update)
    
    def update_status(self, status):
        """Update status label"""
        color = "#4fc1ff" if status == "Running" else "#858585"
        self.stats_labels["status"].config(text=status, foreground=color)
    
    def clear_display(self):
        """Clear the activity display"""
        self.activity_text.delete(1.0, tk.END)
    
    def on_closing(self):
        """Handle window closing"""
        self.running = False
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=1)
        self.root.destroy()


def main():
    """Main entry point"""
    import sys
    
    log_file = sys.argv[1] if len(sys.argv) > 1 else "server.log"
    
    root = tk.Tk()
    app = ServerMonitorGUI(root, log_file)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
