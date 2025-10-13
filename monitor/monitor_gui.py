#!/usr/bin/env python3
"""
Remote GUI Monitor for Server Activity
Real-time visualization of server activity via network
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time
import re
import sys
import os
import socket
from datetime import datetime
from collections import deque

# Add client path for imports
client_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'client')
sys.path.insert(0, client_path)

try:
    from common.byte_buffer import ByteBuffer
    from common.network_client import NetworkClient
    from common.message_types import MSG_MONITOR_FACILITY, MSG_RESPONSE_SUCCESS, MSG_RESPONSE_ERROR
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)


class ServerMonitorGUI:
    """Remote GUI for monitoring server activity"""
    
    def __init__(self, root, server_ip: str, server_port: int):
        self.root = root
        self.server_ip = server_ip
        self.server_port = server_port
        self.network = NetworkClient(server_ip, server_port)
        self.running = False
        self.monitor_thread = None
        self.listen_thread = None
        
        # Statistics
        self.total_requests = 0
        self.total_responses = 0
        self.errors = 0
        self.recent_events = deque(maxlen=100)
        
        # Facilities to monitor
        self.facilities = ['Conference_Room_A', 'Conference_Room_B', 'Lab_101', 'Lab_102', 'Auditorium']
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the GUI interface"""
        self.root.title("Remote Server Monitor")
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
        
        # Facility selection
        facility_frame = ttk.LabelFrame(self.root, text="Facility Selection", padding=10)
        facility_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(facility_frame, text="Facility to Monitor:").grid(row=0, column=0, padx=5, sticky=tk.W)
        self.facility_var = tk.StringVar(value=self.facilities[0])
        facility_combo = ttk.Combobox(facility_frame, textvariable=self.facility_var, values=self.facilities, state="readonly")
        facility_combo.grid(row=0, column=1, padx=5, sticky=tk.W)
        
        # Middle frame - Recent Activity
        activity_frame = ttk.LabelFrame(self.root, text="Server Activity", padding=10)
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
        self.activity_text.tag_config("update", foreground="#9cdcfe")
        
        # Bottom frame - Controls
        control_frame = ttk.Frame(self.root, padding=10)
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.start_button = ttk.Button(control_frame, text="Start Monitoring", command=self.toggle_monitoring)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(control_frame, text="Clear", command=self.clear_display).pack(side=tk.LEFT, padx=5)
        
        # Server info
        ttk.Label(control_frame, text=f"Server: {self.server_ip}:{self.server_port}").pack(side=tk.RIGHT, padx=5)
    
    def toggle_monitoring(self):
        """Start or stop monitoring"""
        if not self.running:
            self.start_monitoring()
        else:
            self.stop_monitoring()
    
    def start_monitoring(self):
        """Start monitoring the server"""
        facility_name = self.facility_var.get()
        
        # Register for monitoring
        if not self.register_monitor(facility_name):
            messagebox.showerror("Error", "Failed to register for monitoring")
            return
        
        self.running = True
        self.start_button.config(text="Stop Monitoring")
        self.update_status("Running")
        
        # Start listening thread
        self.listen_thread = threading.Thread(target=self.listen_for_updates, daemon=True)
        self.listen_thread.start()
        
        self.log_message(f"Started monitoring {facility_name}", "success")
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.running = False
        self.start_button.config(text="Start Monitoring")
        self.update_status("Stopped")
        self.log_message("Stopped monitoring", "error")
    
    def register_monitor(self, facility_name: str) -> bool:
        """Register for monitoring a facility"""
        try:
            # Build request
            request = ByteBuffer()
            request_id = self.network.get_next_request_id()
            request.write_uint32(request_id)
            request.write_uint8(MSG_MONITOR_FACILITY)
            
            payload = ByteBuffer()
            payload.write_string(facility_name)
            payload.write_uint32(3600)  # Monitor for 1 hour
            
            request.write_uint16(len(payload.buffer))
            request.buffer.extend(payload.buffer)
            
            # Send request
            response_data = self.network.send_request(request.get_data())
            if not response_data:
                return False
            
            # Parse response
            response = ByteBuffer(response_data)
            resp_request_id = response.read_uint32()
            status = response.read_uint8()
            
            if status == MSG_RESPONSE_ERROR:
                error_msg = response.read_string()
                self.log_message(f"Registration failed: {error_msg}", "error")
                return False
            
            message = response.read_string()
            self.log_message(f"Registration successful: {message}", "success")
            return True
            
        except Exception as e:
            self.log_message(f"Registration error: {str(e)}", "error")
            return False
    
    def listen_for_updates(self):
        """Listen for server update messages"""
        try:
            while self.running:
                try:
                    # Receive message with timeout
                    self.network.sock.settimeout(1.0)  # 1 second timeout
                    data, addr = self.network.sock.recvfrom(65507)
                    
                    # Process the update
                    self.process_update(data)
                    
                except socket.timeout:
                    continue  # Continue listening
                except Exception as e:
                    if self.running:
                        self.log_message(f"Listen error: {str(e)}", "error")
                    break
                    
        except Exception as e:
            self.log_message(f"Listener stopped: {str(e)}", "error")
    
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
    
    def process_update(self, data):
        """Process a server update message"""
        try:
            response = ByteBuffer(data)
            status = response.read_uint8()
            
            if status == MSG_RESPONSE_SUCCESS:
                message = response.read_string()
                num_slots = response.read_uint16()
                
                update_text = f"{message}\nAvailable slots: {num_slots}\n"
                
                for i in range(num_slots):
                    start_time = response.read_time()
                    end_time = response.read_time()
                    
                    start_dt = datetime.fromtimestamp(start_time)
                    end_dt = datetime.fromtimestamp(end_time)
                    
                    update_text += f"  {i+1}. {start_dt.strftime('%Y-%m-%d %H:%M')} to {end_dt.strftime('%H:%M')}\n"
                
                self.log_message(update_text.strip(), "update")
            else:
                self.log_message("Received error update from server", "error")
                
        except Exception as e:
            self.log_message(f"Error processing update: {str(e)}", "error")


    def on_closing(self):
        """Handle window closing"""
        self.running = False
        if self.listen_thread and self.listen_thread.is_alive():
            self.listen_thread.join(timeout=1)
        self.network.close()
        self.root.destroy()


def main():
    """Main entry point"""
    import sys
    
    # Default to remote server
    server_ip = "8.148.159.175"
    server_port = 8080
    
    if len(sys.argv) >= 2:
        server_ip = sys.argv[1]
    if len(sys.argv) >= 3:
        server_port = int(sys.argv[2])
    
    root = tk.Tk()
    app = ServerMonitorGUI(root, server_ip, server_port)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
