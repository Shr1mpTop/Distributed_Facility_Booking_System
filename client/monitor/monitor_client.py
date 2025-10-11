#!/usr/bin/env python3
"""
Independent Monitor GUI Client
Monitors facility availability changes in real-time
"""

import sys
import os
import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import time
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from common.message_types import *
from common.byte_buffer import ByteBuffer
from common.network_client import NetworkClient


class MonitorGUI:
    def __init__(self, server_host: str, server_port: int):
        self.server_host = server_host
        self.server_port = server_port
        self.network = NetworkClient(server_host, server_port)
        
        # Monitor state
        self.monitoring = False
        self.monitor_thread = None
        
        # Create GUI
        self.root = tk.Tk()
        self.root.title(f"Facility Monitor - {server_host}:{server_port}")
        self.root.geometry("900x700")
        
        self.setup_gui()
        
    def setup_gui(self):
        """Setup the GUI components"""
        # Header
        header = ttk.Frame(self.root, padding="10")
        header.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        ttk.Label(header, text="🔍 Facility Availability Monitor", 
                 font=('Arial', 16, 'bold')).pack(side=tk.LEFT)
        
        # Connection status
        self.status_label = ttk.Label(header, text=f"● Connected to {self.server_host}:{self.server_port}", 
                                     foreground='green', font=('Arial', 10))
        self.status_label.pack(side=tk.RIGHT)
        
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configuration panel
        config_frame = ttk.LabelFrame(main_frame, text="Monitor Configuration", padding="10")
        config_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # Facility selection
        ttk.Label(config_frame, text="Facility:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.facility_combo = ttk.Combobox(config_frame, width=30)
        self.facility_combo['values'] = (
            'Conference_Room_A',
            'Conference_Room_B', 
            'Lab_101',
            'Lab_102',
            'Auditorium'
        )
        self.facility_combo.current(0)
        self.facility_combo.grid(row=0, column=1, padx=5, pady=5)
        
        # Monitor interval
        ttk.Label(config_frame, text="Check Interval (seconds):").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        self.interval_entry = ttk.Entry(config_frame, width=10)
        self.interval_entry.insert(0, "5")
        self.interval_entry.grid(row=0, column=3, padx=5, pady=5)
        
        # Monitor duration
        ttk.Label(config_frame, text="Duration (seconds, 0=infinite):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.duration_entry = ttk.Entry(config_frame, width=10)
        self.duration_entry.insert(0, "60")
        self.duration_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # Days to monitor
        ttk.Label(config_frame, text="Days (comma-separated, 0=today):").grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        self.days_entry = ttk.Entry(config_frame, width=20)
        self.days_entry.insert(0, "0,1,2")
        self.days_entry.grid(row=1, column=3, padx=5, pady=5)
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=1, column=0, pady=10)
        
        self.start_button = ttk.Button(button_frame, text="▶ Start Monitoring", 
                                      command=self.start_monitoring, style='Accent.TButton')
        self.start_button.grid(row=0, column=0, padx=5)
        
        self.stop_button = ttk.Button(button_frame, text="⏹ Stop Monitoring", 
                                     command=self.stop_monitoring, state='disabled')
        self.stop_button.grid(row=0, column=1, padx=5)
        
        ttk.Button(button_frame, text="🗑 Clear Log", 
                  command=self.clear_log).grid(row=0, column=2, padx=5)
        
        # Statistics frame
        stats_frame = ttk.LabelFrame(main_frame, text="Monitor Statistics", padding="10")
        stats_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=5)
        
        self.stats_checks = ttk.Label(stats_frame, text="Checks: 0")
        self.stats_checks.grid(row=0, column=0, padx=10)
        
        self.stats_changes = ttk.Label(stats_frame, text="Changes: 0")
        self.stats_changes.grid(row=0, column=1, padx=10)
        
        self.stats_slots = ttk.Label(stats_frame, text="Current Slots: 0")
        self.stats_slots.grid(row=0, column=2, padx=10)
        
        self.stats_runtime = ttk.Label(stats_frame, text="Running Time: 0s")
        self.stats_runtime.grid(row=0, column=3, padx=10)
        
        # Monitor log
        log_frame = ttk.LabelFrame(main_frame, text="Monitor Log", padding="5")
        log_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=25, width=100,
                                                  font=('Courier', 10))
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure text tags for colored output
        self.log_text.tag_config('info', foreground='black')
        self.log_text.tag_config('success', foreground='green')
        self.log_text.tag_config('warning', foreground='orange')
        self.log_text.tag_config('error', foreground='red')
        self.log_text.tag_config('change', foreground='blue', font=('Courier', 10, 'bold'))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        # Initial log message
        self.log("Monitor client initialized and ready", 'success')
        
    def log(self, message: str, tag='info'):
        """Add message to log with timestamp and color"""
        timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n", tag)
        self.log_text.see(tk.END)
        
    def clear_log(self):
        """Clear the log"""
        self.log_text.delete('1.0', tk.END)
        self.log("Log cleared", 'info')
        
    def start_monitoring(self):
        """Start monitoring in a separate thread"""
        if self.monitoring:
            return
            
        # Disable start button, enable stop button
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.facility_combo.config(state='disabled')
        self.interval_entry.config(state='disabled')
        self.duration_entry.config(state='disabled')
        self.days_entry.config(state='disabled')
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self.monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        facility = self.facility_combo.get()
        self.log(f"▶ Started monitoring '{facility}'", 'success')
        
    def stop_monitoring(self):
        """Stop monitoring"""
        if not self.monitoring:
            return
            
        self.monitoring = False
        
        # Re-enable controls
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.facility_combo.config(state='normal')
        self.interval_entry.config(state='normal')
        self.duration_entry.config(state='normal')
        self.days_entry.config(state='normal')
        
        self.log("⏹ Monitoring stopped", 'warning')
        
    def query_availability(self, facility_name: str, days: list) -> tuple:
        """Query facility availability"""
        try:
            # Build request
            request = ByteBuffer()
            request_id = self.network.get_next_request_id()
            request.write_uint32(request_id)
            request.write_uint8(MSG_QUERY_AVAILABILITY)
            
            payload = ByteBuffer()
            payload.write_string(facility_name)
            payload.write_uint16(len(days))
            for day in days:
                payload.write_uint32(day)
            
            request.write_uint16(len(payload.buffer))
            request.buffer.extend(payload.buffer)
            
            # Send request
            response_data = self.network.send_request(request.get_data(), timeout=3.0)
            if not response_data:
                return None, "Request timeout"
            
            # Parse response
            response = ByteBuffer(response_data)
            resp_request_id = response.read_uint32()
            status = response.read_uint8()
            
            if status == MSG_RESPONSE_ERROR:
                error_msg = response.read_string()
                return None, error_msg
            
            # Read available slots
            num_slots = response.read_uint16()
            slots = []
            for _ in range(num_slots):
                start_time = response.read_uint32()
                end_time = response.read_uint32()
                slots.append((start_time, end_time))
            
            return slots, None
            
        except Exception as e:
            return None, str(e)
            
    def monitor_loop(self):
        """Main monitoring loop"""
        facility_name = self.facility_combo.get()
        days_str = self.days_entry.get().strip()
        days = [int(d.strip()) for d in days_str.split(',')]
        
        try:
            interval = float(self.interval_entry.get())
            duration = float(self.duration_entry.get())
        except ValueError:
            self.log("Invalid interval or duration", 'error')
            self.root.after(0, self.stop_monitoring)
            return
        
        infinite = (duration == 0)
        start_time = time.time()
        check_count = 0
        change_count = 0
        previous_slots = None
        
        self.log(f"Monitoring parameters: interval={interval}s, duration={'infinite' if infinite else f'{duration}s'}, days={days}", 'info')
        self.log("-" * 80, 'info')
        
        while self.monitoring:
            if not infinite and (time.time() - start_time) > duration:
                self.log("Duration reached, stopping monitor", 'warning')
                self.root.after(0, self.stop_monitoring)
                break
            
            # Query availability
            check_count += 1
            slots, error = self.query_availability(facility_name, days)
            
            if error:
                self.log(f"Check #{check_count} - ERROR: {error}", 'error')
            else:
                # Detect changes
                if previous_slots is not None and slots != previous_slots:
                    change_count += 1
                    self.log(f"Check #{check_count} - 🔔 CHANGE DETECTED! Available slots changed from {len(previous_slots)} to {len(slots)}", 'change')
                    
                    # Show differences
                    removed = set(previous_slots) - set(slots)
                    added = set(slots) - set(previous_slots)
                    
                    if removed:
                        self.log(f"  ↓ Removed: {len(removed)} slot(s)", 'warning')
                        for slot in removed:
                            self.log(f"    - {datetime.fromtimestamp(slot[0]).strftime('%Y-%m-%d %H:%M')} to {datetime.fromtimestamp(slot[1]).strftime('%H:%M')}", 'warning')
                    
                    if added:
                        self.log(f"  ↑ Added: {len(added)} slot(s)", 'success')
                        for slot in added:
                            self.log(f"    + {datetime.fromtimestamp(slot[0]).strftime('%Y-%m-%d %H:%M')} to {datetime.fromtimestamp(slot[1]).strftime('%H:%M')}", 'success')
                else:
                    self.log(f"Check #{check_count} - No changes detected ({len(slots)} slots available)", 'info')
                
                previous_slots = slots
            
            # Update statistics
            runtime = int(time.time() - start_time)
            self.root.after(0, lambda: self.update_stats(check_count, change_count, len(slots) if slots else 0, runtime))
            
            # Wait for next check
            if self.monitoring:
                time.sleep(interval)
        
        self.log("-" * 80, 'info')
        self.log(f"Monitoring session completed: {check_count} checks, {change_count} changes detected", 'success')
        
    def update_stats(self, checks, changes, slots, runtime):
        """Update statistics display"""
        self.stats_checks.config(text=f"Checks: {checks}")
        self.stats_changes.config(text=f"Changes: {changes}")
        self.stats_slots.config(text=f"Current Slots: {slots}")
        self.stats_runtime.config(text=f"Running Time: {runtime}s")
        
    def run(self):
        """Start the GUI main loop"""
        self.root.mainloop()


def main():
    if len(sys.argv) < 3:
        print("Usage: python3 monitor_client.py <server_host> <server_port>")
        print("Example: python3 monitor_client.py localhost 8080")
        sys.exit(1)
    
    server_host = sys.argv[1]
    server_port = int(sys.argv[2])
    
    monitor = MonitorGUI(server_host, server_port)
    monitor.run()


if __name__ == '__main__':
    main()
