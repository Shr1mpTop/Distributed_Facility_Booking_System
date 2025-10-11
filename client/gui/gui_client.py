#!/usr/bin/env python3
"""
Facility Booking System - GUI Client
GUI client using tkinter
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import sys
import os
from datetime import datetime, timedelta
from typing import List, Tuple
import threading

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.byte_buffer import ByteBuffer
from common.network_client import NetworkClient
from common.message_types import *


class FacilityBookingGUI:
    """Main GUI client class"""
    
    def __init__(self, server_ip: str, server_port: int):
        self.network = NetworkClient(server_ip, server_port)
        
        # Create main window
        self.root = tk.Tk()
        self.root.title("Facility Booking System - Client")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        # Set style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Create interface
        self.create_widgets()
        
    def create_widgets(self):
        """Create all GUI components with a modern, academic, React-like style"""
        self.root.configure(bg="#f7f7fa")
        # Top bar
        top_bar = tk.Frame(self.root, bg="#22223b", height=56)
        top_bar.grid(row=0, column=0, sticky="nsew")
        top_bar.grid_propagate(False)
        tk.Label(top_bar, text="Facility Booking System", fg="#fff", bg="#22223b", font=("Segoe UI", 18, "bold"), anchor="w").pack(side=tk.LEFT, padx=24, pady=8)
        tk.Label(top_bar, text=f"Server: {self.network.server_ip}:{self.network.server_port}", fg="#c9ada7", bg="#22223b", font=("Segoe UI", 11), anchor="e").pack(side=tk.RIGHT, padx=24)

        # Main content area
        main_frame = tk.Frame(self.root, bg="#f7f7fa")
        main_frame.grid(row=1, column=0, sticky="nsew", padx=0, pady=(0,0))
        self.root.rowconfigure(1, weight=1)
        self.root.columnconfigure(0, weight=1)

        # Left navigation (vertical tabs)
        nav_frame = tk.Frame(main_frame, bg="#f7f7fa", width=180)
        nav_frame.grid(row=0, column=0, sticky="nsw")
        nav_frame.grid_propagate(False)
        nav_btn_style = {"font": ("Segoe UI", 12), "bg": "#f7f7fa", "fg": "#22223b", "activebackground": "#e0e1dd", "bd": 0, "relief": "flat", "anchor": "w", "padx": 18, "pady": 12}
        self.active_tab = tk.StringVar(value="Query")
        tabs = [
            ("Query", "Query Availability"),
            ("Book", "Book Facility"),
            ("Change", "Change Booking"),
            ("Ops", "Operations")
        ]
        for i, (key, label) in enumerate(tabs):
            b = tk.Radiobutton(nav_frame, text=label, variable=self.active_tab, value=key, indicatoron=0, **nav_btn_style, selectcolor="#4a4e69")
            b.grid(row=i, column=0, sticky="ew")

        # Content area
        content_frame = tk.Frame(main_frame, bg="#fff", bd=0, highlightbackground="#e0e1dd", highlightthickness=1)
        content_frame.grid(row=0, column=1, sticky="nsew", padx=(0,0), pady=(0,0))
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)

        # Section frames
        self.section_frames = {}
        for key in ["Query", "Book", "Change", "Ops"]:
            f = tk.Frame(content_frame, bg="#fff")
            f.grid(row=0, column=0, sticky="nsew")
            self.section_frames[key] = f
        self.create_query_tab(self.section_frames["Query"])
        self.create_book_tab(self.section_frames["Book"])
        self.create_change_tab(self.section_frames["Change"])
        self.create_operations_tab(self.section_frames["Ops"])
        self.show_section("Query")
        self.active_tab.trace_add("write", lambda *_: self.show_section(self.active_tab.get()))

        # Log area (bottom, always visible)
        log_frame = tk.Frame(self.root, bg="#22223b", height=120)
        log_frame.grid(row=2, column=0, sticky="ew")
        log_frame.grid_propagate(False)
        tk.Label(log_frame, text="Log", fg="#fff", bg="#22223b", font=("Segoe UI", 11, "bold"), anchor="w").pack(side=tk.TOP, anchor="w", padx=16, pady=(8,0))
        self.log_text = scrolledtext.ScrolledText(log_frame, height=5, state='disabled', bg="#23243a", fg="#e0e1dd", font=("Consolas", 10), borderwidth=0, highlightthickness=0)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=16, pady=(0,12))
        self.root.rowconfigure(2, minsize=120)

    def show_section(self, key):
        for k, f in self.section_frames.items():
            if k == key:
                f.tkraise()
            else:
                f.lower()
        
    def create_query_tab(self, parent):
        """Modern query availability section"""
        frame = parent
        # Title
        tk.Label(frame, text="Query Facility Availability", font=("Segoe UI", 15, "bold"), bg="#fff", fg="#22223b").grid(row=0, column=0, columnspan=2, sticky="w", pady=(18,8), padx=24)
        # Facility name
        tk.Label(frame, text="Facility Name:", font=("Segoe UI", 11), bg="#fff").grid(row=1, column=0, sticky="e", pady=6, padx=(24,8))
        self.query_facility = ttk.Combobox(frame, width=28, font=("Segoe UI", 11))
        self.query_facility['values'] = ('Conference_Room_A', 'Conference_Room_B', 'Lab_101', 'Lab_102', 'Auditorium')
        self.query_facility.grid(row=1, column=1, pady=6, sticky="w")
        self.query_facility.current(0)
        # Query days
        tk.Label(frame, text="Query Days (comma separated, 0=today):", font=("Segoe UI", 11), bg="#fff").grid(row=2, column=0, sticky="e", pady=6, padx=(24,8))
        self.query_days = tk.Entry(frame, width=30, font=("Segoe UI", 11))
        self.query_days.insert(0, "0,1,2")
        self.query_days.grid(row=2, column=1, pady=6, sticky="w")
        # Query button
        tk.Button(frame, text="Query", command=self.query_availability, font=("Segoe UI", 11, "bold"), bg="#4a4e69", fg="#fff", activebackground="#9a8c98", activeforeground="#fff", relief="flat", padx=18, pady=6).grid(row=3, column=0, columnspan=2, pady=16)
        # Results display
        tk.Label(frame, text="Available Time Slots:", font=("Segoe UI", 11, "bold"), bg="#fff").grid(row=4, column=0, sticky="nw", padx=(24,8), pady=(8,0))
        self.query_result = scrolledtext.ScrolledText(frame, height=10, width=60, font=("Consolas", 10), bg="#f7f7fa", fg="#22223b", borderwidth=0, highlightthickness=1, highlightbackground="#e0e1dd")
        self.query_result.grid(row=5, column=0, columnspan=2, padx=24, pady=(0,18), sticky="ew")
        frame.columnconfigure(1, weight=1)
        
    def create_book_tab(self, parent):
        """Modern booking section"""
        frame = parent
        # Title
        tk.Label(frame, text="Book Facility", font=("Segoe UI", 15, "bold"), bg="#fff", fg="#22223b").grid(row=0, column=0, columnspan=2, sticky="w", pady=(18,8), padx=24)
        
        # Facility name
        tk.Label(frame, text="Facility Name:", font=("Segoe UI", 11), bg="#fff").grid(row=1, column=0, sticky="e", pady=6, padx=(24,8))
        self.book_facility = ttk.Combobox(frame, width=28, font=("Segoe UI", 11))
        self.book_facility['values'] = ('Conference_Room_A', 'Conference_Room_B', 'Lab_101', 'Lab_102', 'Auditorium')
        self.book_facility.grid(row=1, column=1, pady=6, sticky="w")
        self.book_facility.current(0)
        
        # Date
        tk.Label(frame, text="Date (YYYY-MM-DD):", font=("Segoe UI", 11), bg="#fff").grid(row=2, column=0, sticky="e", pady=6, padx=(24,8))
        self.book_date = tk.Entry(frame, width=30, font=("Segoe UI", 11))
        self.book_date.insert(0, datetime.now().strftime('%Y-%m-%d'))
        self.book_date.grid(row=2, column=1, pady=6, sticky="w")
        
        # Time
        tk.Label(frame, text="Start Time (HH:MM):", font=("Segoe UI", 11), bg="#fff").grid(row=3, column=0, sticky="e", pady=6, padx=(24,8))
        self.book_time = tk.Entry(frame, width=30, font=("Segoe UI", 11))
        self.book_time.insert(0, "09:00")
        self.book_time.grid(row=3, column=1, pady=6, sticky="w")
        
        # Duration
        tk.Label(frame, text="Duration (hours):", font=("Segoe UI", 11), bg="#fff").grid(row=4, column=0, sticky="e", pady=6, padx=(24,8))
        self.book_duration = tk.Entry(frame, width=30, font=("Segoe UI", 11))
        self.book_duration.insert(0, "1")
        self.book_duration.grid(row=4, column=1, pady=6, sticky="w")
        
        # Book button
        tk.Button(frame, text="Book Facility", command=self.book_facility_action, font=("Segoe UI", 11, "bold"), bg="#4a4e69", fg="#fff", activebackground="#9a8c98", activeforeground="#fff", relief="flat", padx=18, pady=6).grid(row=5, column=0, columnspan=2, pady=16)
        
        # Results display
        tk.Label(frame, text="Booking Result:", font=("Segoe UI", 11, "bold"), bg="#fff").grid(row=6, column=0, sticky="nw", padx=(24,8), pady=(8,0))
        self.book_result = scrolledtext.ScrolledText(frame, height=8, width=60, font=("Consolas", 10), bg="#f7f7fa", fg="#22223b", borderwidth=0, highlightthickness=1, highlightbackground="#e0e1dd")
        self.book_result.grid(row=7, column=0, columnspan=2, padx=24, pady=(0,18), sticky="ew")
        frame.columnconfigure(1, weight=1)
        
    def create_change_tab(self, parent):
        """Modern change booking section"""
        frame = parent
        # Title
        tk.Label(frame, text="Change Booking", font=("Segoe UI", 15, "bold"), bg="#fff", fg="#22223b").grid(row=0, column=0, columnspan=2, sticky="w", pady=(18,8), padx=24)
        
        # Confirmation ID
        tk.Label(frame, text="Confirmation ID:", font=("Segoe UI", 11), bg="#fff").grid(row=1, column=0, sticky="e", pady=6, padx=(24,8))
        self.change_id = tk.Entry(frame, width=30, font=("Segoe UI", 11))
        self.change_id.grid(row=1, column=1, pady=6, sticky="w")
        
        # Time offset
        tk.Label(frame, text="Time Offset (minutes):", font=("Segoe UI", 11), bg="#fff").grid(row=2, column=0, sticky="e", pady=6, padx=(24,8))
        self.change_offset = tk.Entry(frame, width=30, font=("Segoe UI", 11))
        self.change_offset.insert(0, "30")
        self.change_offset.grid(row=2, column=1, pady=6, sticky="w")
        
        tk.Label(frame, text="(Positive for later, negative for earlier)", font=("Segoe UI", 9, "italic"), bg="#fff", fg="#666").grid(row=3, column=1, sticky="w", padx=0)
        
        # Change button
        tk.Button(frame, text="Change Booking", command=self.change_booking, font=("Segoe UI", 11, "bold"), bg="#4a4e69", fg="#fff", activebackground="#9a8c98", activeforeground="#fff", relief="flat", padx=18, pady=6).grid(row=4, column=0, columnspan=2, pady=16)
        
        # Results display
        tk.Label(frame, text="Change Result:", font=("Segoe UI", 11, "bold"), bg="#fff").grid(row=5, column=0, sticky="nw", padx=(24,8), pady=(8,0))
        self.change_result = scrolledtext.ScrolledText(frame, height=8, width=60, font=("Consolas", 10), bg="#f7f7fa", fg="#22223b", borderwidth=0, highlightthickness=1, highlightbackground="#e0e1dd")
        self.change_result.grid(row=6, column=0, columnspan=2, padx=24, pady=(0,18), sticky="ew")
        frame.columnconfigure(1, weight=1)
        
    def create_operations_tab(self, parent):
        """Modern operations section"""
        frame = parent
        # Title
        tk.Label(frame, text="Additional Operations", font=("Segoe UI", 15, "bold"), bg="#fff", fg="#22223b").grid(row=0, column=0, columnspan=2, sticky="w", pady=(18,8), padx=24)
        
        # Get last booking time section
        tk.Label(frame, text="Get Last Booking Time (Idempotent)", font=("Segoe UI", 12, "bold"), bg="#fff", fg="#4a4e69").grid(row=1, column=0, columnspan=2, sticky="w", pady=(12,6), padx=24)
        
        tk.Label(frame, text="Facility Name:", font=("Segoe UI", 11), bg="#fff").grid(row=2, column=0, sticky="e", pady=6, padx=(24,8))
        self.last_time_facility = ttk.Combobox(frame, width=28, font=("Segoe UI", 11))
        self.last_time_facility['values'] = ('Conference_Room_A', 'Conference_Room_B', 'Lab_101', 'Lab_102', 'Auditorium')
        self.last_time_facility.grid(row=2, column=1, pady=6, sticky="w")
        self.last_time_facility.current(0)
        
        tk.Button(frame, text="Query Last Booking Time", command=self.get_last_booking_time, font=("Segoe UI", 10, "bold"), bg="#6c757d", fg="#fff", activebackground="#9a8c98", activeforeground="#fff", relief="flat", padx=14, pady=4).grid(row=3, column=0, columnspan=2, pady=10)
        
        # Separator
        ttk.Separator(frame, orient='horizontal').grid(row=4, column=0, columnspan=2, sticky="ew", padx=24, pady=12)
        
        # Extend booking section
        tk.Label(frame, text="Extend Booking (Non-Idempotent)", font=("Segoe UI", 12, "bold"), bg="#fff", fg="#4a4e69").grid(row=5, column=0, columnspan=2, sticky="w", pady=(6,6), padx=24)
        
        tk.Label(frame, text="Confirmation ID:", font=("Segoe UI", 11), bg="#fff").grid(row=6, column=0, sticky="e", pady=6, padx=(24,8))
        self.extend_id = tk.Entry(frame, width=30, font=("Segoe UI", 11))
        self.extend_id.grid(row=6, column=1, pady=6, sticky="w")
        
        tk.Label(frame, text="Extension Time (minutes):", font=("Segoe UI", 11), bg="#fff").grid(row=7, column=0, sticky="e", pady=6, padx=(24,8))
        self.extend_minutes = tk.Entry(frame, width=30, font=("Segoe UI", 11))
        self.extend_minutes.insert(0, "30")
        self.extend_minutes.grid(row=7, column=1, pady=6, sticky="w")
        
        tk.Button(frame, text="Extend Booking", command=self.extend_booking, font=("Segoe UI", 10, "bold"), bg="#6c757d", fg="#fff", activebackground="#9a8c98", activeforeground="#fff", relief="flat", padx=14, pady=4).grid(row=8, column=0, columnspan=2, pady=10)
        
        # Results display
        tk.Label(frame, text="Operation Result:", font=("Segoe UI", 11, "bold"), bg="#fff").grid(row=9, column=0, sticky="nw", padx=(24,8), pady=(8,0))
        self.ops_result = scrolledtext.ScrolledText(frame, height=8, width=60, font=("Consolas", 10), bg="#f7f7fa", fg="#22223b", borderwidth=0, highlightthickness=1, highlightbackground="#e0e1dd")
        self.ops_result.grid(row=10, column=0, columnspan=2, padx=24, pady=(0,18), sticky="ew")
        frame.columnconfigure(1, weight=1)
        
    def log(self, message: str):
        """Add log message"""
        self.log_text.config(state='normal')
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')
        
    def query_availability(self):
        """Query availability"""
        try:
            facility_name = self.query_facility.get().strip()
            days_input = self.query_days.get().strip()
            days = [int(d.strip()) for d in days_input.split(',')]
            
            self.log(f"Querying availability for {facility_name}...")
            
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
            response_data = self.network.send_request(request.get_data())
            if not response_data:
                self.query_result.delete('1.0', tk.END)
                self.query_result.insert(tk.END, "Request timeout\n")
                self.log("Request timeout")
                return
            
            # Parse response
            response = ByteBuffer(response_data)
            resp_request_id = response.read_uint32()
            status = response.read_uint8()
            
            if status == MSG_RESPONSE_ERROR:
                error_msg = response.read_string()
                self.query_result.delete('1.0', tk.END)
                self.query_result.insert(tk.END, f"Error: {error_msg}\n")
                self.log(f"Error: {error_msg}")
                return
            
            # Read available time slots
            num_slots = response.read_uint16()
            result_text = f"Found {num_slots} available time slots:\n\n"
            
            for i in range(num_slots):
                start_time = response.read_time()
                end_time = response.read_time()
                
                start_dt = datetime.fromtimestamp(start_time)
                end_dt = datetime.fromtimestamp(end_time)
                
                result_text += f"{i+1}. {start_dt.strftime('%Y-%m-%d %H:%M')} to {end_dt.strftime('%H:%M')}\n"
            
            self.query_result.delete('1.0', tk.END)
            self.query_result.insert(tk.END, result_text)
            self.log(f"Query successful, found {num_slots} time slots")
            
        except Exception as e:
            messagebox.showerror("Error", f"Query failed: {str(e)}")
            self.log(f"Error: {str(e)}")
            
    def book_facility_action(self):
        """Book facility"""
        try:
            facility_name = self.book_facility.get().strip()
            date_str = self.book_date.get().strip()
            time_str = self.book_time.get().strip()
            duration_hours = float(self.book_duration.get().strip())
            
            # Parse time
            start_dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
            start_time = int(start_dt.timestamp())
            end_time = start_time + int(duration_hours * 3600)
            
            self.log(f"Booking {facility_name}...")
            
            # Build request
            request = ByteBuffer()
            request_id = self.network.get_next_request_id()
            request.write_uint32(request_id)
            request.write_uint8(MSG_BOOK_FACILITY)
            
            payload = ByteBuffer()
            payload.write_string(facility_name)
            payload.write_time(start_time)
            payload.write_time(end_time)
            
            request.write_uint16(len(payload.buffer))
            request.buffer.extend(payload.buffer)
            
            # Send request
            response_data = self.network.send_request(request.get_data())
            if not response_data:
                self.book_result.delete('1.0', tk.END)
                self.book_result.insert(tk.END, "Request timeout\n")
                self.log("Request timeout")
                return
            
            # Parse response
            response = ByteBuffer(response_data)
            resp_request_id = response.read_uint32()
            status = response.read_uint8()
            
            if status == MSG_RESPONSE_ERROR:
                error_msg = response.read_string()
                self.book_result.delete('1.0', tk.END)
                self.book_result.insert(tk.END, f"Booking failed: {error_msg}\n")
                self.log(f"Booking failed: {error_msg}")
                return
            
            # Read confirmation ID
            confirmation_id = response.read_uint32()
            result_text = f"✓ BookingSuccess!\n\n"
            result_text += f"Confirmation ID: {confirmation_id}\n"
            result_text += f"Facility: {facility_name}\n"
            result_text += f"Time: {start_dt.strftime('%Y-%m-%d %H:%M')} to {datetime.fromtimestamp(end_time).strftime('%H:%M')}\n"
            
            self.book_result.delete('1.0', tk.END)
            self.book_result.insert(tk.END, result_text)
            self.log(f"BookingSuccess，Confirmation ID: {confirmation_id}")
            messagebox.showinfo("Success", f"BookingSuccess！Confirmation ID: {confirmation_id}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Booking failed: {str(e)}")
            self.log(f"Error: {str(e)}")
            
    def change_booking(self):
        """Change booking"""
        try:
            confirmation_id = int(self.change_id.get().strip())
            offset_minutes = int(self.change_offset.get().strip())
            
            self.log(f"Change booking ID {confirmation_id}...")
            
            # Build request
            request = ByteBuffer()
            request_id = self.network.get_next_request_id()
            request.write_uint32(request_id)
            request.write_uint8(MSG_CHANGE_BOOKING)
            
            payload = ByteBuffer()
            payload.write_uint32(confirmation_id)
            payload.write_uint32(offset_minutes & 0xFFFFFFFF)
            
            request.write_uint16(len(payload.buffer))
            request.buffer.extend(payload.buffer)
            
            # Send request
            response_data = self.network.send_request(request.get_data())
            if not response_data:
                self.change_result.delete('1.0', tk.END)
                self.change_result.insert(tk.END, "Request timeout\n")
                self.log("Request timeout")
                return
            
            # Parse response
            response = ByteBuffer(response_data)
            resp_request_id = response.read_uint32()
            status = response.read_uint8()
            
            if status == MSG_RESPONSE_ERROR:
                error_msg = response.read_string()
                self.change_result.delete('1.0', tk.END)
                self.change_result.insert(tk.END, f"Change failed: {error_msg}\n")
                self.log(f"Change failed: {error_msg}")
                return
            
            message = response.read_string()
            self.change_result.delete('1.0', tk.END)
            self.change_result.insert(tk.END, f"✓ {message}\n")
            self.log("Booking changed successfully")
            messagebox.showinfo("Success", message)
            
        except Exception as e:
            messagebox.showerror("Error", f"Change failed: {str(e)}")
            self.log(f"Error: {str(e)}")
            
    def get_last_booking_time(self):
        """Get last booking time"""
        try:
            facility_name = self.last_time_facility.get().strip()
            
            self.log(f"Querying {facility_name} last booking time...")
            
            # Build request
            request = ByteBuffer()
            request_id = self.network.get_next_request_id()
            request.write_uint32(request_id)
            request.write_uint8(MSG_GET_LAST_BOOKING_TIME)
            
            payload = ByteBuffer()
            payload.write_string(facility_name)
            
            request.write_uint16(len(payload.buffer))
            request.buffer.extend(payload.buffer)
            
            # Send request
            response_data = self.network.send_request(request.get_data())
            if not response_data:
                self.ops_result.delete('1.0', tk.END)
                self.ops_result.insert(tk.END, "Request timeout\n")
                self.log("Request timeout")
                return
            
            # Parse response
            response = ByteBuffer(response_data)
            resp_request_id = response.read_uint32()
            status = response.read_uint8()
            
            if status == MSG_RESPONSE_ERROR:
                error_msg = response.read_string()
                self.ops_result.delete('1.0', tk.END)
                self.ops_result.insert(tk.END, f"Error: {error_msg}\n")
                self.log(f"Error: {error_msg}")
                return
            
            last_time = response.read_time()
            message = response.read_string()
            
            result_text = f"Facility: {facility_name}\n"
            if last_time == 0:
                result_text += f"{message}\n"
            else:
                last_dt = datetime.fromtimestamp(last_time)
                result_text += f"Last booking end time: {last_dt.strftime('%Y-%m-%d %H:%M:%S')}\n"
                result_text += f"Status: {message}\n"
            
            self.ops_result.delete('1.0', tk.END)
            self.ops_result.insert(tk.END, result_text)
            self.log("QueryingSuccess")
            
        except Exception as e:
            messagebox.showerror("Error", f"Query failed: {str(e)}")
            self.log(f"Error: {str(e)}")
            
    def extend_booking(self):
        """Extend booking"""
        try:
            confirmation_id = int(self.extend_id.get().strip())
            minutes_to_extend = int(self.extend_minutes.get().strip())
            
            self.log(f"Extend booking ID {confirmation_id}...")
            
            # Build request
            request = ByteBuffer()
            request_id = self.network.get_next_request_id()
            request.write_uint32(request_id)
            request.write_uint8(MSG_EXTEND_BOOKING)
            
            payload = ByteBuffer()
            payload.write_uint32(confirmation_id)
            payload.write_uint32(minutes_to_extend)
            
            request.write_uint16(len(payload.buffer))
            request.buffer.extend(payload.buffer)
            
            # Send request
            response_data = self.network.send_request(request.get_data())
            if not response_data:
                self.ops_result.delete('1.0', tk.END)
                self.ops_result.insert(tk.END, "Request timeout\n")
                self.log("Request timeout")
                return
            
            # Parse response
            response = ByteBuffer(response_data)
            resp_request_id = response.read_uint32()
            status = response.read_uint8()
            
            if status == MSG_RESPONSE_ERROR:
                error_msg = response.read_string()
                self.ops_result.delete('1.0', tk.END)
                self.ops_result.insert(tk.END, f"Extension failed: {error_msg}\n")
                self.log(f"Extension failed: {error_msg}")
                return
            
            new_end_time = response.read_time()
            message = response.read_string()
            
            new_end_dt = datetime.fromtimestamp(new_end_time)
            result_text = f"✓ {message}\n"
            result_text += f"New end time: {new_end_dt.strftime('%Y-%m-%d %H:%M:%S')}\n"
            
            self.ops_result.delete('1.0', tk.END)
            self.ops_result.insert(tk.END, result_text)
            self.log("Extension successful")
            messagebox.showinfo("Success", message)
            
        except Exception as e:
            messagebox.showerror("Error", f"Extension failed: {str(e)}")
            self.log(f"Error: {str(e)}")
            
    def run(self):
        """Run GUI main loop"""
        self.log("Client started")
        self.root.mainloop()
        self.network.close()


def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <server_ip> <server_port>")
        sys.exit(1)
    
    server_ip = sys.argv[1]
    server_port = int(sys.argv[2])
    
    app = FacilityBookingGUI(server_ip, server_port)
    app.run()


if __name__ == '__main__':
    main()
