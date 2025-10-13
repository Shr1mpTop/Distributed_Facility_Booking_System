#!/usr/bin/env python3
"""
Facility Booking System - GUI Client
GUI client using tkinter
"""

import tkinter as tk
import sys
import os
from datetime import datetime, timedelta
from typing import List, Tuple
import threading
from tkinter import ttk, scrolledtext, messagebox

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.byte_buffer import ByteBuffer
from common.network_client import NetworkClient
from common.message_types import *

class TimeTableView(tk.Frame):
    """Time table view component"""
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.configure(bg='white')
        self.selected_days = set(range(7))  # 默认选中所有天
        self.day_buttons = []
        self._create_timetable()
        
    def _create_timetable(self):
        """Creates the timetable using grid layout for proper alignment."""
        # Configure the grid columns to have equal weight, allowing them to resize.
        # Column 0 is for the time, and columns 1-7 are for the days.
        self.columnconfigure(0, weight=0)  # Time column has a fixed size
        for i in range(1, 8):
            self.columnconfigure(i, weight=1)

        # --- HEADER ---
        # Time column header - minimal style
        tk.Label(
            self, 
            text="Time", 
            bg='#fafafa', 
            fg='#666666',
            font=('Helvetica Neue', 9, 'bold')
        ).grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        
        # Day column headers (now as toggle buttons) - clean style
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        today = datetime.now()
        
        self.day_buttons = []
        for i, day in enumerate(days):
            date = today + timedelta(days=i)
            label_text = f"{day}\n{date.strftime('%m/%d')}"
            
            btn = tk.Button(
                self, 
                text=label_text, 
                bg='#1a1a1a',  # 默认选中颜色 - 深色
                fg='white',
                font=('Helvetica Neue', 9),
                relief='flat',
                borderwidth=0,
                command=lambda d=i: self.toggle_day(d),
                cursor="hand2",
                padx=8,
                pady=8
            )
            btn.grid(row=0, column=i + 1, sticky="ew", padx=1, pady=0)
            self.day_buttons.append(btn)
            
        # --- TIME SLOTS ---
        self.time_slots = {}
        times = [f"{h:02d}:00" for h in range(8, 23)]
        for i, time in enumerate(times):
            # Time label in the first column - minimal
            tk.Label(
                self, 
                text=time, 
                width=6, 
                bg='#fafafa', 
                fg='#999999',
                font=('Monaco', 8)
            ).grid(row=i + 1, column=0, sticky="ew", padx=0, pady=0)
            
            # Availability slots for each day - clean borders
            for day_index in range(7):
                slot = tk.Label(
                    self, 
                    text="", 
                    bg='white', 
                    relief='flat',
                    borderwidth=0,
                    highlightthickness=1,
                    highlightbackground='#f0f0f0',
                    font=('Helvetica Neue', 8)
                )
                slot.grid(row=i + 1, column=day_index + 1, sticky="nsew", padx=0, pady=0)
                self.time_slots[f"{day_index}-{time}"] = slot
    
    def toggle_day(self, day_index):
        """切换日期选择状态"""
        if day_index in self.selected_days:
            self.selected_days.remove(day_index)
            self.day_buttons[day_index].config(bg='#e8e8e8', fg='#999999')
        else:
            self.selected_days.add(day_index)
            self.day_buttons[day_index].config(bg='#1a1a1a', fg='white')
        
        # 更新列的高亮显示
        self.update_column_highlight()
    
    def update_column_highlight(self):
        """更新列的高亮显示"""
        for day_index in range(7):
            is_selected = day_index in self.selected_days
            for time_key, slot in self.time_slots.items():
                if time_key.startswith(f"{day_index}-"):
                    if not slot.cget('text'):  # 如果是空白格子
                        if is_selected:
                            slot.config(bg='#fafafa', highlightbackground='#e0e0e0')  # 高亮背景
                        else:
                            slot.config(bg='#f5f5f5', highlightbackground='#eeeeee')  # 灰色背景
    
    def get_selected_days(self):
        """获取选中的天数"""
        return sorted(list(self.selected_days))
                
    def clear_bookings(self):
        """清除所有预订显示"""
        for slot in self.time_slots.values():
            slot.config(text="", bg='white')
        self.update_column_highlight()
            
    def add_booking(self, day: int, start_time: str, end_time: str, facility: str, booking_id: str = ""):
        """添加一个预订显示"""
        start_hour = int(start_time.split(':')[0])
        end_hour = int(end_time.split(':')[0])
        
        for hour in range(start_hour, end_hour + 1):
            time_key = f"{day}-{hour:02d}:00"
            if time_key in self.time_slots:
                # 简约的深色标记
                display_text = f"#{booking_id}" if booking_id else "●"
                self.time_slots[time_key].config(
                    text=display_text,
                    bg='#1a1a1a',
                    fg='#ffffff',
                    highlightbackground='#1a1a1a'
                )
    
    def mark_available(self, day: int, start_time: str, end_time: str):
        """标记可用时间段"""
        start_hour = int(start_time.split(':')[0])
        end_hour = int(end_time.split(':')[0])
        
        for hour in range(start_hour, end_hour + 1):
            time_key = f"{day}-{hour:02d}:00"
            if time_key in self.time_slots:
                # 简约的绿色标记
                self.time_slots[time_key].config(
                    text="○",
                    bg='#e8f5e9',
                    fg='#4caf50',
                    highlightbackground='#c8e6c9'
                )

class FacilityBookingGUI:
    """Main GUI client class"""
    
    def __init__(self, server_ip: str, server_port: int):
        self.network = NetworkClient(server_ip, server_port)
        
        # Create main window
        self.root = tk.Tk()
        self.root.title("设施预订系统")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        self.root.resizable(True, True)
        
        # Set style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configure colors
        self.colors = {
            'primary': '#1976d2',
            'primary_dark': '#1565c0',
            'secondary': '#78909c',
            'background': '#ffffff',
            'surface': '#f5f5f5',
            'error': '#d32f2f',
            'success': '#2e7d32',
            'text': '#212121',
            'text_secondary': '#757575'
        }
        
        # Create interface
        self.create_widgets()
    """Main GUI client class"""
    
    def __init__(self, server_ip: str, server_port: int):
        self.network = NetworkClient(server_ip, server_port)
        
        # Monitoring state
        self.monitoring = False
        self.monitor_thread = None
        
        # Create main window
        self.root = tk.Tk()
        self.root.title("设施预订系统")
        self.root.geometry("1200x800")
        self.root.resizable(True, True)
        
        # Set style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Create interface
        self.create_widgets()
        
    def create_widgets(self):
        """Create all GUI components with a clean, minimalist style"""
        self.root.configure(bg="#ffffff")
        
        # Top bar - Simple and clean
        top_bar = tk.Frame(self.root, bg="#ffffff", height=60)
        top_bar.grid(row=0, column=0, sticky="nsew")
        top_bar.grid_propagate(False)
        
        # Title with minimal decoration
        tk.Label(
            top_bar, 
            text="Facility Booking", 
            fg="#1a1a1a", 
            bg="#ffffff", 
            font=("Helvetica Neue", 20, "bold")
        ).pack(side=tk.LEFT, padx=30, pady=15)
        
        # Server info - subtle
        tk.Label(
            top_bar, 
            text=f"{self.network.server_ip}:{self.network.server_port}", 
            fg="#999999", 
            bg="#ffffff", 
            font=("Helvetica Neue", 10)
        ).pack(side=tk.RIGHT, padx=30)
        
        # Thin separator line
        separator = tk.Frame(self.root, bg="#e5e5e5", height=1)
        separator.grid(row=1, column=0, sticky="ew")

        # Main content area
        main_frame = tk.Frame(self.root, bg="#ffffff")
        main_frame.grid(row=2, column=0, sticky="nsew", padx=0, pady=0)
        self.root.rowconfigure(2, weight=1)
        self.root.columnconfigure(0, weight=1)

        # Left navigation - Minimalist tabs
        nav_frame = tk.Frame(main_frame, bg="#fafafa", width=160)
        nav_frame.grid(row=0, column=0, sticky="nsw", padx=0, pady=0)
        nav_frame.grid_propagate(False)
        
        self.active_tab = tk.StringVar(value="Query")
        tabs = [
            ("Query", "Schedule"),
            ("Book", "New Booking"),
            ("Change", "Modify"),
            ("Ops", "More"),
            ("Monitor", "Monitor")
        ]
        
        self.nav_buttons = []
        for i, (key, label) in enumerate(tabs):
            btn = tk.Button(
                nav_frame,
                text=label,
                command=lambda k=key: self.switch_tab(k),
                font=("Helvetica Neue", 11),
                bg="#fafafa" if i != 0 else "#1a1a1a",
                fg="#666666" if i != 0 else "#ffffff",
                activebackground="#f0f0f0",
                activeforeground="#1a1a1a",
                bd=0,
                relief="flat",
                anchor="w",
                padx=20,
                pady=14,
                cursor="hand2"
            )
            btn.grid(row=i, column=0, sticky="ew", pady=1)
            self.nav_buttons.append(btn)

        # Content area - Clean white background
        content_frame = tk.Frame(main_frame, bg="#ffffff")
        content_frame.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)

        # Section frames
        self.section_frames = {}
        for key in ["Query", "Book", "Change", "Ops", "Monitor"]:
            f = tk.Frame(content_frame, bg="#ffffff")
            f.grid(row=0, column=0, sticky="nsew")
            content_frame.rowconfigure(0, weight=1)
            content_frame.columnconfigure(0, weight=1)
            self.section_frames[key] = f
            
        self.create_query_tab(self.section_frames["Query"])
        self.create_book_tab(self.section_frames["Book"])
        self.create_change_tab(self.section_frames["Change"])
        self.create_operations_tab(self.section_frames["Ops"])
        self.create_monitor_tab(self.section_frames["Monitor"])
        self.show_section("Query")

        # Log area - Minimal and clean
        log_frame = tk.Frame(self.root, bg="#fafafa", height=100)
        log_frame.grid(row=3, column=0, sticky="ew")
        log_frame.grid_propagate(False)
        
        tk.Label(
            log_frame, 
            text="Activity Log", 
            fg="#666666", 
            bg="#fafafa", 
            font=("Helvetica Neue", 10)
        ).pack(side=tk.TOP, anchor="w", padx=20, pady=(8,4))
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame, 
            height=4, 
            state='disabled', 
            bg="#ffffff", 
            fg="#333333", 
            font=("Monaco", 9),
            borderwidth=1,
            highlightthickness=0,
            relief="flat"
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0,10))
        self.root.rowconfigure(3, minsize=100)
    
    def switch_tab(self, key):
        """Switch tab with visual feedback"""
        self.active_tab.set(key)
        self.show_section(key)
        
        # Update nav button styles
        tabs_keys = ["Query", "Book", "Change", "Ops"]
        for i, btn in enumerate(self.nav_buttons):
            if tabs_keys[i] == key:
                btn.config(bg="#1a1a1a", fg="#ffffff")
            else:
                btn.config(bg="#fafafa", fg="#666666")

    def show_section(self, key):
        for k, f in self.section_frames.items():
            if k == key:
                f.tkraise()
            else:
                f.lower()
        
    def create_query_tab(self, parent):
        """Minimalist query availability section"""
        frame = parent
        frame.configure(bg="#ffffff")
        
        # Container with padding
        container = tk.Frame(frame, bg="#ffffff")
        container.pack(fill=tk.BOTH, expand=True, padx=40, pady=30)
        
        # Facility selection - clean pills
        tk.Label(
            container, 
            text="Facilities", 
            font=("Helvetica Neue", 12), 
            bg="#ffffff",
            fg="#666666"
        ).pack(anchor="w", pady=(0,10))
        
        facility_btn_frame = tk.Frame(container, bg="#ffffff")
        facility_btn_frame.pack(anchor="w", pady=(0,20))
        
        facilities = ['Conference_Room_A', 'Conference_Room_B', 'Lab_101', 'Lab_102', 'Auditorium']
        self.selected_facility = tk.StringVar(value=facilities[0])
        self.facility_buttons = []
        
        for i, facility in enumerate(facilities):
            btn = tk.Button(
                facility_btn_frame,
                text=facility.replace('_', ' '),
                command=lambda f=facility: self.select_facility(f),
                font=("Helvetica Neue", 10),
                bg="#1a1a1a" if i == 0 else "#f5f5f5",
                fg="white" if i == 0 else "#666666",
                activebackground="#333333",
                activeforeground="#ffffff",
                relief="flat",
                borderwidth=0,
                padx=16,
                pady=8,
                cursor="hand2"
            )
            btn.pack(side=tk.LEFT, padx=(0,8))
            self.facility_buttons.append(btn)
        
        # 时间表显示
        tk.Label(
            container, 
            text="Weekly Schedule", 
            font=("Helvetica Neue", 12), 
            bg="#ffffff",
            fg="#666666"
        ).pack(anchor="w", pady=(10,10))
        
        timetable_frame = tk.Frame(container, bg="#ffffff", relief="flat", borderwidth=0)
        timetable_frame.pack(fill=tk.BOTH, expand=True)
        
        self.timetable = TimeTableView(timetable_frame, bg="white")
        self.timetable.pack(fill=tk.BOTH, expand=True)
    
    def select_facility(self, facility_name):
        """选择设施"""
        self.selected_facility.set(facility_name)
        # 更新按钮样式 - 简约风格
        facilities = ['Conference_Room_A', 'Conference_Room_B', 'Lab_101', 'Lab_102', 'Auditorium']
        for i, btn in enumerate(self.facility_buttons):
            if facilities[i] == facility_name:
                btn.config(bg="#1a1a1a", fg="white")
            else:
                btn.config(bg="#f5f5f5", fg="#666666")
        # 自动刷新
        self.query_availability()
    
    def select_book_facility(self, facility_name):
        """选择预订设施"""
        self.selected_book_facility.set(facility_name)
        # 更新按钮样式 - 简约风格
        facilities = ['Conference_Room_A', 'Conference_Room_B', 'Lab_101', 'Lab_102', 'Auditorium']
        for i, btn in enumerate(self.book_facility_buttons):
            if facilities[i] == facility_name:
                btn.config(bg="#1a1a1a", fg="white")
            else:
                btn.config(bg="#f5f5f5", fg="#666666")
        
    def create_book_tab(self, parent):
        """Minimalist booking section"""
        frame = parent
        frame.configure(bg="#ffffff")
        
        # Container with padding
        container = tk.Frame(frame, bg="#ffffff")
        container.pack(fill=tk.BOTH, expand=True, padx=40, pady=30)
        
        # Form container
        form_frame = tk.Frame(container, bg="#ffffff")
        form_frame.pack(fill=tk.X, pady=(0,20))
        
        # Facility selection
        tk.Label(
            form_frame, 
            text="Facility", 
            font=("Helvetica Neue", 11), 
            bg="#ffffff",
            fg="#666666"
        ).grid(row=0, column=0, sticky="w", pady=(0,8))
        
        book_facility_btn_frame = tk.Frame(form_frame, bg="#ffffff")
        book_facility_btn_frame.grid(row=1, column=0, sticky="w", pady=(0,16))
        
        facilities = ['Conference_Room_A', 'Conference_Room_B', 'Lab_101', 'Lab_102', 'Auditorium']
        self.selected_book_facility = tk.StringVar(value=facilities[0])
        self.book_facility_buttons = []
        
        for i, facility in enumerate(facilities):
            btn = tk.Button(
                book_facility_btn_frame,
                text=facility.replace('_', ' '),
                command=lambda f=facility: self.select_book_facility(f),
                font=("Helvetica Neue", 9),
                bg="#1a1a1a" if i == 0 else "#f5f5f5",
                fg="white" if i == 0 else "#666666",
                activebackground="#333333",
                activeforeground="#ffffff",
                relief="flat",
                borderwidth=0,
                padx=12,
                pady=6,
                cursor="hand2"
            )
            btn.pack(side=tk.LEFT, padx=(0,6))
            self.book_facility_buttons.append(btn)
        
        # Date input
        tk.Label(
            form_frame, 
            text="Date", 
            font=("Helvetica Neue", 11), 
            bg="#ffffff",
            fg="#666666"
        ).grid(row=2, column=0, sticky="w", pady=(0,8))
        
        self.book_date = tk.Entry(
            form_frame, 
            width=40, 
            font=("Helvetica Neue", 11),
            bg="#fafafa",
            fg="#1a1a1a",
            relief="flat",
            borderwidth=1,
            highlightthickness=1,
            highlightbackground="#e0e0e0"
        )
        self.book_date.insert(0, datetime.now().strftime('%Y-%m-%d'))
        self.book_date.grid(row=3, column=0, sticky="w", pady=(0,16))
        
        # Time input
        tk.Label(
            form_frame, 
            text="Start Time", 
            font=("Helvetica Neue", 11), 
            bg="#ffffff",
            fg="#666666"
        ).grid(row=4, column=0, sticky="w", pady=(0,8))
        
        self.book_time = tk.Entry(
            form_frame, 
            width=40, 
            font=("Helvetica Neue", 11),
            bg="#fafafa",
            fg="#1a1a1a",
            relief="flat",
            borderwidth=1,
            highlightthickness=1,
            highlightbackground="#e0e0e0"
        )
        self.book_time.insert(0, "09:00")
        self.book_time.grid(row=5, column=0, sticky="w", pady=(0,16))
        
        # Duration input
        tk.Label(
            form_frame, 
            text="Duration (hours)", 
            font=("Helvetica Neue", 11), 
            bg="#ffffff",
            fg="#666666"
        ).grid(row=6, column=0, sticky="w", pady=(0,8))
        
        self.book_duration = tk.Entry(
            form_frame, 
            width=40, 
            font=("Helvetica Neue", 11),
            bg="#fafafa",
            fg="#1a1a1a",
            relief="flat",
            borderwidth=1,
            highlightthickness=1,
            highlightbackground="#e0e0e0"
        )
        self.book_duration.insert(0, "1")
        self.book_duration.grid(row=7, column=0, sticky="w", pady=(0,20))
        
        # Book button
        tk.Button(
            form_frame, 
            text="Create Booking", 
            command=self.book_facility_action, 
            font=("Helvetica Neue", 11, "bold"), 
            bg="#1a1a1a", 
            fg="#ffffff", 
            activebackground="#333333", 
            activeforeground="#ffffff", 
            relief="flat",
            borderwidth=0,
            padx=24,
            pady=10,
            cursor="hand2"
        ).grid(row=8, column=0, sticky="w", pady=(0,20))
        
        # Results display
        self.book_result = scrolledtext.ScrolledText(
            container, 
            height=6, 
            width=60, 
            font=("Monaco", 9), 
            bg="#fafafa", 
            fg="#333333", 
            borderwidth=0, 
            highlightthickness=0,
            relief="flat"
        )
        self.book_result.pack(fill=tk.X)
        
    def create_change_tab(self, parent):
        """Minimalist change booking section"""
        frame = parent
        frame.configure(bg="#ffffff")
        
        # Container with padding
        container = tk.Frame(frame, bg="#ffffff")
        container.pack(fill=tk.BOTH, expand=True, padx=40, pady=30)
        
        # Form container
        form_frame = tk.Frame(container, bg="#ffffff")
        form_frame.pack(fill=tk.X, pady=(0,20))
        
        # Confirmation ID
        tk.Label(
            form_frame, 
            text="Booking ID", 
            font=("Helvetica Neue", 11), 
            bg="#ffffff",
            fg="#666666"
        ).grid(row=0, column=0, sticky="w", pady=(0,8))
        
        self.change_id = tk.Entry(
            form_frame, 
            width=40, 
            font=("Helvetica Neue", 11),
            bg="#fafafa",
            fg="#1a1a1a",
            relief="flat",
            borderwidth=1,
            highlightthickness=1,
            highlightbackground="#e0e0e0"
        )
        self.change_id.grid(row=1, column=0, sticky="w", pady=(0,16))
        
        # Time offset
        tk.Label(
            form_frame, 
            text="Time Offset (minutes)", 
            font=("Helvetica Neue", 11), 
            bg="#ffffff",
            fg="#666666"
        ).grid(row=2, column=0, sticky="w", pady=(0,8))
        
        self.change_offset = tk.Entry(
            form_frame, 
            width=40, 
            font=("Helvetica Neue", 11),
            bg="#fafafa",
            fg="#1a1a1a",
            relief="flat",
            borderwidth=1,
            highlightthickness=1,
            highlightbackground="#e0e0e0"
        )
        self.change_offset.insert(0, "30")
        self.change_offset.grid(row=3, column=0, sticky="w", pady=(0,6))
        
        tk.Label(
            form_frame, 
            text="+ for later, - for earlier", 
            font=("Helvetica Neue", 9), 
            bg="#ffffff", 
            fg="#999999"
        ).grid(row=4, column=0, sticky="w", pady=(0,20))
        
        # Change button
        tk.Button(
            form_frame, 
            text="Update Booking", 
            command=self.change_booking, 
            font=("Helvetica Neue", 11, "bold"), 
            bg="#1a1a1a", 
            fg="#ffffff", 
            activebackground="#333333", 
            activeforeground="#ffffff", 
            relief="flat",
            borderwidth=0,
            padx=24,
            pady=10,
            cursor="hand2"
        ).grid(row=5, column=0, sticky="w", pady=(0,20))
        
        # Results display
        self.change_result = scrolledtext.ScrolledText(
            container, 
            height=6, 
            width=60, 
            font=("Monaco", 9), 
            bg="#fafafa", 
            fg="#333333", 
            borderwidth=0, 
            highlightthickness=0,
            relief="flat"
        )
        self.change_result.pack(fill=tk.X)
        
    def create_operations_tab(self, parent):
        """Minimalist operations section"""
        frame = parent
        frame.configure(bg="#ffffff")
        
        # Container with padding
        container = tk.Frame(frame, bg="#ffffff")
        container.pack(fill=tk.BOTH, expand=True, padx=40, pady=30)
        
        # Section 1: Get Last Booking Time
        section1 = tk.Frame(container, bg="#ffffff")
        section1.pack(fill=tk.X, pady=(0,30))
        
        tk.Label(
            section1, 
            text="Last Booking Query", 
            font=("Helvetica Neue", 12), 
            bg="#ffffff",
            fg="#666666"
        ).pack(anchor="w", pady=(0,12))
        
        tk.Label(
            section1, 
            text="Facility", 
            font=("Helvetica Neue", 10), 
            bg="#ffffff",
            fg="#999999"
        ).pack(anchor="w", pady=(0,6))
        
        self.last_time_facility = ttk.Combobox(
            section1, 
            width=38, 
            font=("Helvetica Neue", 10)
        )
        self.last_time_facility['values'] = ('Conference_Room_A', 'Conference_Room_B', 'Lab_101', 'Lab_102', 'Auditorium')
        self.last_time_facility.pack(anchor="w", pady=(0,12))
        self.last_time_facility.current(0)
        
        tk.Button(
            section1, 
            text="Query", 
            command=self.get_last_booking_time, 
            font=("Helvetica Neue", 10, "bold"), 
            bg="#1a1a1a", 
            fg="#ffffff", 
            activebackground="#333333", 
            activeforeground="#ffffff", 
            relief="flat",
            borderwidth=0,
            padx=20,
            pady=8,
            cursor="hand2"
        ).pack(anchor="w")
        
        # Separator
        tk.Frame(container, bg="#e5e5e5", height=1).pack(fill=tk.X, pady=20)
        
        # Section 2: Extend Booking
        section2 = tk.Frame(container, bg="#ffffff")
        section2.pack(fill=tk.X, pady=(0,20))
        
        tk.Label(
            section2, 
            text="Extend Booking", 
            font=("Helvetica Neue", 12), 
            bg="#ffffff",
            fg="#666666"
        ).pack(anchor="w", pady=(0,12))
        
        tk.Label(
            section2, 
            text="Booking ID", 
            font=("Helvetica Neue", 10), 
            bg="#ffffff",
            fg="#999999"
        ).pack(anchor="w", pady=(0,6))
        
        self.extend_id = tk.Entry(
            section2, 
            width=40, 
            font=("Helvetica Neue", 11),
            bg="#fafafa",
            fg="#1a1a1a",
            relief="flat",
            borderwidth=1,
            highlightthickness=1,
            highlightbackground="#e0e0e0"
        )
        self.extend_id.pack(anchor="w", pady=(0,12))
        
        tk.Label(
            section2, 
            text="Extension (minutes)", 
            font=("Helvetica Neue", 10), 
            bg="#ffffff",
            fg="#999999"
        ).pack(anchor="w", pady=(0,6))
        
        self.extend_minutes = tk.Entry(
            section2, 
            width=40, 
            font=("Helvetica Neue", 11),
            bg="#fafafa",
            fg="#1a1a1a",
            relief="flat",
            borderwidth=1,
            highlightthickness=1,
            highlightbackground="#e0e0e0"
        )
        self.extend_minutes.insert(0, "30")
        self.extend_minutes.pack(anchor="w", pady=(0,12))
        
        tk.Button(
            section2, 
            text="Extend", 
            command=self.extend_booking, 
            font=("Helvetica Neue", 10, "bold"), 
            bg="#1a1a1a", 
            fg="#ffffff", 
            activebackground="#333333", 
            activeforeground="#ffffff", 
            relief="flat",
            borderwidth=0,
            padx=20,
            pady=8,
            cursor="hand2"
        ).pack(anchor="w")
        
        # Results display
        self.ops_result = scrolledtext.ScrolledText(
            container, 
            height=6, 
            width=60, 
            font=("Monaco", 9), 
            bg="#fafafa", 
            fg="#333333", 
            borderwidth=0, 
            highlightthickness=0,
            relief="flat"
        )
        self.ops_result.pack(fill=tk.X, pady=(20,0))
        
    def create_monitor_tab(self, parent):
        """Monitor facility availability tab"""
        frame = parent
        frame.configure(bg="#ffffff")
        
        # Container with padding
        container = tk.Frame(frame, bg="#ffffff")
        container.pack(fill=tk.BOTH, expand=True, padx=40, pady=30)
        
        # Title
        tk.Label(
            container, 
            text="Real-time Facility Monitor", 
            font=("Helvetica Neue", 14, "bold"), 
            bg="#ffffff",
            fg="#1a1a1a"
        ).pack(anchor="w", pady=(0,20))
        
        # Description
        tk.Label(
            container, 
            text="Monitor a facility for real-time availability updates.\nNote: During monitoring, other operations will be disabled.", 
            font=("Helvetica Neue", 10), 
            bg="#ffffff",
            fg="#999999",
            justify=tk.LEFT
        ).pack(anchor="w", pady=(0,20))
        
        # Facility selection
        tk.Label(
            container, 
            text="Facility to Monitor", 
            font=("Helvetica Neue", 10), 
            bg="#ffffff",
            fg="#999999"
        ).pack(anchor="w", pady=(0,6))
        
        self.monitor_facility = ttk.Combobox(
            container, 
            width=38, 
            font=("Helvetica Neue", 10)
        )
        self.monitor_facility['values'] = ('Conference_Room_A', 'Conference_Room_B', 'Lab_101', 'Lab_102', 'Auditorium')
        self.monitor_facility.pack(anchor="w", pady=(0,12))
        self.monitor_facility.current(0)
        
        # Monitor duration
        tk.Label(
            container, 
            text="Monitor Duration (seconds)", 
            font=("Helvetica Neue", 10), 
            bg="#ffffff",
            fg="#999999"
        ).pack(anchor="w", pady=(0,6))
        
        self.monitor_duration = tk.Entry(
            container, 
            width=40, 
            font=("Helvetica Neue", 11),
            bg="#fafafa",
            fg="#1a1a1a",
            relief="flat",
            borderwidth=1,
            highlightthickness=1,
            highlightbackground="#e0e0e0"
        )
        self.monitor_duration.insert(0, "300")
        self.monitor_duration.pack(anchor="w", pady=(0,20))
        
        # Control buttons frame
        button_frame = tk.Frame(container, bg="#ffffff")
        button_frame.pack(anchor="w", pady=(0,20))
        
        self.start_monitor_btn = tk.Button(
            button_frame, 
            text="Start Monitoring", 
            command=self.start_monitoring, 
            font=("Helvetica Neue", 10, "bold"), 
            bg="#1a1a1a", 
            fg="#ffffff", 
            activebackground="#333333", 
            activeforeground="#ffffff", 
            relief="flat",
            borderwidth=0,
            padx=20,
            pady=8,
            cursor="hand2"
        )
        self.start_monitor_btn.pack(side=tk.LEFT, padx=(0,10))
        
        self.stop_monitor_btn = tk.Button(
            button_frame, 
            text="Stop Monitoring", 
            command=self.stop_monitoring, 
            font=("Helvetica Neue", 10, "bold"), 
            bg="#666666", 
            fg="#ffffff", 
            activebackground="#999999", 
            activeforeground="#ffffff", 
            relief="flat",
            borderwidth=0,
            padx=20,
            pady=8,
            cursor="hand2",
            state=tk.DISABLED
        )
        self.stop_monitor_btn.pack(side=tk.LEFT)
        
        # Monitor status
        self.monitor_status = tk.Label(
            container, 
            text="Status: Not monitoring", 
            font=("Helvetica Neue", 10), 
            bg="#ffffff",
            fg="#999999"
        )
        self.monitor_status.pack(anchor="w", pady=(0,12))
        
        # Results display
        tk.Label(
            container, 
            text="Availability Updates", 
            font=("Helvetica Neue", 10, "bold"), 
            bg="#ffffff",
            fg="#666666"
        ).pack(anchor="w", pady=(0,8))
        
        self.monitor_result = scrolledtext.ScrolledText(
            container, 
            height=12, 
            width=60, 
            font=("Monaco", 9), 
            bg="#fafafa", 
            fg="#333333", 
            borderwidth=0, 
            highlightthickness=0,
            relief="flat"
        )
        self.monitor_result.pack(fill=tk.BOTH, expand=True, pady=(0,0))
        
    def log(self, message: str):
        """Add log message"""
        self.log_text.config(state='normal')
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')
        
    def query_availability(self):
        """Query availability and display in timetable"""
        try:
            facility_name = self.selected_facility.get().strip()
            days = self.timetable.get_selected_days()  # 从时间表获取选中的天数
            
            self.log(f"正在查询 {facility_name} 的可用时段 (天数: {days})...")
            self.timetable.clear_bookings()  # 清除之前的显示
            
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
                self.log("请求超时")
                return
            
            # Parse response
            response = ByteBuffer(response_data)
            resp_request_id = response.read_uint32()
            status = response.read_uint8()
            
            if status == MSG_RESPONSE_ERROR:
                error_msg = response.read_string()
                self.log(f"错误: {error_msg}")
                return
            
            # Read and display available time slots
            num_slots = response.read_uint16()
            
            for i in range(num_slots):
                start_time = response.read_time()
                end_time = response.read_time()
                
                start_dt = datetime.fromtimestamp(start_time)
                end_dt = datetime.fromtimestamp(end_time)
                
                # 计算相对于今天的天数
                today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                slot_day = (start_dt.replace(hour=0, minute=0, second=0, microsecond=0) - today).days
                
                # 在时间表中标记可用时段
                if 0 <= slot_day <= 6:  # 只显示一周内的时段
                    self.timetable.mark_available(
                        slot_day,
                        start_dt.strftime('%H:%M'),
                        end_dt.strftime('%H:%M')
                    )
            
            self.log(f"查询成功，找到 {num_slots} 个可用时段")
            
            # 更新列的高亮显示
            self.timetable.update_column_highlight()

            # 在显示可用时段后，获取并显示我的预订
            self._fetch_and_display_my_bookings()
            
        except Exception as e:
            messagebox.showerror("Error", f"Query failed: {str(e)}")
            self.log(f"Error: {str(e)}")

    def _fetch_and_display_my_bookings(self):
        """获取并显示当前用户的所有预订
        
        注意：此功能需要服务器支持 GET_MY_BOOKINGS 消息类型
        目前服务器未实现此功能，因此此方法不执行任何操作
        """
        # 服务器当前不支持获取用户预订列表的功能
        # 预订信息会在查询可用性时通过其他方式显示
        pass
            
    def book_facility_action(self):
        """Book facility"""
        try:
            facility_name = self.selected_book_facility.get().strip()
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
            
            # 自动刷新查询结果
            self.query_availability()
            
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
    
    def start_monitoring(self):
        """Start monitoring a facility"""
        if self.monitoring:
            messagebox.showwarning("Warning", "Already monitoring")
            return
        
        try:
            facility_name = self.monitor_facility.get().strip()
            duration = int(self.monitor_duration.get().strip())
            
            self.log(f"Registering monitor for {facility_name}...")
            
            # Build request
            request = ByteBuffer()
            request_id = self.network.get_next_request_id()
            request.write_uint32(request_id)
            request.write_uint8(MSG_MONITOR_FACILITY)
            
            payload = ByteBuffer()
            payload.write_string(facility_name)
            payload.write_uint32(duration)
            
            request.write_uint16(len(payload.buffer))
            request.buffer.extend(payload.buffer)
            
            # Send request
            response_data = self.network.send_request(request.get_data())
            if not response_data:
                self.monitor_result.delete('1.0', tk.END)
                self.monitor_result.insert(tk.END, "Request timeout\n")
                self.log("Request timeout")
                return
            
            # Parse response
            response = ByteBuffer(response_data)
            resp_request_id = response.read_uint32()
            status = response.read_uint8()
            
            if status == MSG_RESPONSE_ERROR:
                error_msg = response.read_string()
                self.monitor_result.delete('1.0', tk.END)
                self.monitor_result.insert(tk.END, f"Registration failed: {error_msg}\n")
                self.log(f"Registration failed: {error_msg}")
                return
            
            message = response.read_string()
            self.monitor_result.delete('1.0', tk.END)
            self.monitor_result.insert(tk.END, f"✓ {message}\n")
            self.monitor_result.insert(tk.END, f"Monitoring {facility_name} for {duration} seconds\n\n")
            self.log(f"Monitoring started: {facility_name}")
            
            # Start monitoring
            self.monitoring = True
            self.start_monitor_btn.config(state=tk.DISABLED)
            self.stop_monitor_btn.config(state=tk.NORMAL)
            self.monitor_facility.config(state=tk.DISABLED)
            self.monitor_duration.config(state=tk.DISABLED)
            self.monitor_status.config(text=f"Status: Monitoring {facility_name}", fg="#4a9c2d")
            
            # Disable other tabs
            for i, btn in enumerate(self.nav_buttons):
                if i != 4:  # Keep Monitor tab enabled
                    btn.config(state=tk.DISABLED)
            
            # Start listening thread
            self.monitor_thread = threading.Thread(target=self.monitor_listen, daemon=True)
            self.monitor_thread.start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start monitoring: {str(e)}")
            self.log(f"Error: {str(e)}")
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.monitoring = False
        self.start_monitor_btn.config(state=tk.NORMAL)
        self.stop_monitor_btn.config(state=tk.DISABLED)
        self.monitor_facility.config(state="readonly")
        self.monitor_duration.config(state=tk.NORMAL)
        self.monitor_status.config(text="Status: Not monitoring", fg="#999999")
        
        # Re-enable other tabs
        for btn in self.nav_buttons:
            btn.config(state=tk.NORMAL)
        
        self.log("Monitoring stopped")
    
    def monitor_listen(self):
        """Listen for monitor updates from server"""
        import socket
        try:
            while self.monitoring:
                try:
                    # Set timeout to check monitoring flag periodically
                    self.network.sock.settimeout(1.0)
                    data, addr = self.network.sock.recvfrom(65507)
                    
                    # Process update
                    self.process_monitor_update(data)
                    
                except socket.timeout:
                    continue
                except Exception as e:
                    if self.monitoring:
                        self.log(f"Listen error: {str(e)}")
                    break
        except Exception as e:
            self.log(f"Monitor thread error: {str(e)}")
        finally:
            if self.monitoring:
                self.root.after(0, self.stop_monitoring)
    
    def process_monitor_update(self, data):
        """Process a monitor update from server"""
        try:
            response = ByteBuffer(data)
            request_id = response.read_uint32()
            status = response.read_uint8()
            
            if status == MSG_RESPONSE_SUCCESS:
                message = response.read_string()
                num_slots = response.read_uint16()
                
                update_text = f"\n[{datetime.now().strftime('%H:%M:%S')}] {message}\n"
                update_text += f"Available slots: {num_slots}\n"
                
                for i in range(num_slots):
                    start_time = response.read_time()
                    end_time = response.read_time()
                    
                    start_dt = datetime.fromtimestamp(start_time)
                    end_dt = datetime.fromtimestamp(end_time)
                    
                    update_text += f"  {i+1}. {start_dt.strftime('%Y-%m-%d %H:%M')} to {end_dt.strftime('%H:%M')}\n"
                
                # Update display in main thread
                self.root.after(0, lambda: self._update_monitor_display(update_text))
            else:
                self.root.after(0, lambda: self._update_monitor_display("\n[Error] Received error from server\n"))
                
        except Exception as e:
            self.root.after(0, lambda: self._update_monitor_display(f"\n[Error] Failed to process update: {str(e)}\n"))
    
    def _update_monitor_display(self, text):
        """Update monitor display (must be called from main thread)"""
        self.monitor_result.insert(tk.END, text)
        self.monitor_result.see(tk.END)
            
    def run(self):
        """Run GUI main loop"""
        self.log("Client started")
        # 启动后自动加载第一周的数据
        self.root.after(500, self.query_availability)
        self.root.mainloop()
        self.network.close()


def main():
    # Fixed server IP and port
    server_ip = "8.148.159.175"
    server_port = 8080
    
    # Allow override from command line
    if len(sys.argv) >= 2:
        server_ip = sys.argv[1]
    if len(sys.argv) >= 3:
        server_port = int(sys.argv[2])
    
    app = FacilityBookingGUI(server_ip, server_port)
    app.run()


if __name__ == '__main__':
    main()
