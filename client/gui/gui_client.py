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
        """Create all GUI components"""
        
        # Top info bar
        top_frame = ttk.Frame(self.root, padding="10")
        top_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        ttk.Label(top_frame, text=f"Server: {self.network.server_ip}:{self.network.server_port}", 
                 font=('Arial', 10, 'bold')).pack()
        
        # Main container
        main_container = ttk.Notebook(self.root, padding="10")
        main_container.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=5)
        
        # Configure row and column weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)
        
        # Create functional tabs
        self.create_query_tab(main_container)
        self.create_book_tab(main_container)
        self.create_change_tab(main_container)
        self.create_monitor_tab(main_container)
        self.create_operations_tab(main_container)
        
        # Bottom log area
        log_frame = ttk.LabelFrame(self.root, text="Log", padding="5")
        log_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.S), padx=10, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=8, state='disabled')
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        self.root.rowconfigure(2, weight=1)
        
    def create_query_tab(self, notebook):
        """Create query availability tab"""
        frame = ttk.Frame(notebook, padding="10")
        notebook.add(frame, text="Query Availability")
        
        # Facility name
        ttk.Label(frame, text="Facility Name:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.query_facility = ttk.Combobox(frame, width=30)
        self.query_facility['values'] = ('Conference_Room_A', 'Conference_Room_B', 
                                         'Lab_101', 'Lab_102', 'Auditorium')
        self.query_facility.grid(row=0, column=1, pady=5, padx=5)
        self.query_facility.current(0)
        
        # Query days
        ttk.Label(frame, text="Query Days (comma separated, 0=today):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.query_days = ttk.Entry(frame, width=32)
        self.query_days.insert(0, "0,1,2")
        self.query_days.grid(row=1, column=1, pady=5, padx=5)
        
        # Query button
        ttk.Button(frame, text="Query", command=self.query_availability, 
                  style='Accent.TButton').grid(row=2, column=0, columnspan=2, pady=10)
        
        # Results display
        ttk.Label(frame, text="Available Time Slots:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.query_result = scrolledtext.ScrolledText(frame, height=15, width=70)
        self.query_result.grid(row=4, column=0, columnspan=2, pady=5)
        
    def create_book_tab(self, notebook):
        """Create booking tab"""
        frame = ttk.Frame(notebook, padding="10")
        notebook.add(frame, text="Book Facility")
        
        # Facility name
        ttk.Label(frame, text="Facility Name:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.book_facility = ttk.Combobox(frame, width=30)
        self.book_facility['values'] = ('Conference_Room_A', 'Conference_Room_B', 
                                        'Lab_101', 'Lab_102', 'Auditorium')
        self.book_facility.grid(row=0, column=1, pady=5, padx=5)
        self.book_facility.current(0)
        
        # Date
        ttk.Label(frame, text="Date (YYYY-MM-DD):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.book_date = ttk.Entry(frame, width=32)
        self.book_date.insert(0, datetime.now().strftime('%Y-%m-%d'))
        self.book_date.grid(row=1, column=1, pady=5, padx=5)
        
        # Time
        ttk.Label(frame, text="Start Time (HH:MM):").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.book_time = ttk.Entry(frame, width=32)
        self.book_time.insert(0, "09:00")
        self.book_time.grid(row=2, column=1, pady=5, padx=5)
        
        # Duration
        ttk.Label(frame, text="Duration (hours):").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.book_duration = ttk.Entry(frame, width=32)
        self.book_duration.insert(0, "1")
        self.book_duration.grid(row=3, column=1, pady=5, padx=5)
        
        # Book button
        ttk.Button(frame, text="Book", command=self.book_facility_action,
                  style='Accent.TButton').grid(row=4, column=0, columnspan=2, pady=10)
        
        # Results display
        self.book_result = scrolledtext.ScrolledText(frame, height=10, width=70)
        self.book_result.grid(row=5, column=0, columnspan=2, pady=5)
        
    def create_change_tab(self, notebook):
        """Create change booking tab"""
        frame = ttk.Frame(notebook, padding="10")
        notebook.add(frame, text="Change Booking")
        
        # Confirmation ID
        ttk.Label(frame, text="Confirmation ID:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.change_id = ttk.Entry(frame, width=32)
        self.change_id.grid(row=0, column=1, pady=5, padx=5)
        
        # Time offset
        ttk.Label(frame, text="Time Offset (minutes):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.change_offset = ttk.Entry(frame, width=32)
        self.change_offset.insert(0, "30")
        self.change_offset.grid(row=1, column=1, pady=5, padx=5)
        
        ttk.Label(frame, text="(Positive for later, negative for earlier)", 
                 font=('Arial', 9, 'italic')).grid(row=2, column=1, sticky=tk.W)
        
        # Change button
        ttk.Button(frame, text="Change Booking", command=self.change_booking,
                  style='Accent.TButton').grid(row=3, column=0, columnspan=2, pady=10)
        
        # Results display
        self.change_result = scrolledtext.ScrolledText(frame, height=10, width=70)
        self.change_result.grid(row=4, column=0, columnspan=2, pady=5)
        
    def create_monitor_tab(self, notebook):
        """Create monitor tab"""
        frame = ttk.Frame(notebook, padding="10")
        notebook.add(frame, text="Monitor Facility")
        
        # Facility name
        ttk.Label(frame, text="Facility Name:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.monitor_facility = ttk.Combobox(frame, width=30)
        self.monitor_facility['values'] = ('Conference_Room_A', 'Conference_Room_B', 
                                           'Lab_101', 'Lab_102', 'Auditorium')
        self.monitor_facility.grid(row=0, column=1, pady=5, padx=5)
        self.monitor_facility.current(0)
        
        # Monitor duration
        ttk.Label(frame, text="Monitor Duration (seconds):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.monitor_duration = ttk.Entry(frame, width=32)
        self.monitor_duration.insert(0, "60")
        self.monitor_duration.grid(row=1, column=1, pady=5, padx=5)
        
        # Monitor button
        self.monitor_button = ttk.Button(frame, text="Start Monitoring", 
                                        command=self.monitor_facility_action)
        self.monitor_button.grid(row=2, column=0, columnspan=2, pady=10)
        
        # Results display
        ttk.Label(frame, text="Monitor Updates:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.monitor_result = scrolledtext.ScrolledText(frame, height=15, width=70)
        self.monitor_result.grid(row=4, column=0, columnspan=2, pady=5)
        
    def create_operations_tab(self, notebook):
        """Create operations tab"""
        frame = ttk.Frame(notebook, padding="10")
        notebook.add(frame, text="Operations")
        
        # Get last booking time
        group1 = ttk.LabelFrame(frame, text="Get Last Booking Time (Idempotent Operation)", padding="10")
        group1.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(group1, text="Facility Name:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.last_time_facility = ttk.Combobox(group1, width=25)
        self.last_time_facility['values'] = ('Conference_Room_A', 'Conference_Room_B', 
                                             'Lab_101', 'Lab_102', 'Auditorium')
        self.last_time_facility.grid(row=0, column=1, pady=5, padx=5)
        self.last_time_facility.current(0)
        
        ttk.Button(group1, text="Query", command=self.get_last_booking_time).grid(row=1, column=0, columnspan=2, pady=5)
        
        # Extend booking
        group2 = ttk.LabelFrame(frame, text="Extend Booking (Non-Idempotent Operation)", padding="10")
        group2.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(group2, text="Confirmation ID:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.extend_id = ttk.Entry(group2, width=27)
        self.extend_id.grid(row=0, column=1, pady=5, padx=5)
        
        ttk.Label(group2, text="Extension Time (minutes):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.extend_minutes = ttk.Entry(group2, width=27)
        self.extend_minutes.insert(0, "30")
        self.extend_minutes.grid(row=1, column=1, pady=5, padx=5)
        
        ttk.Button(group2, text="Extend", command=self.extend_booking).grid(row=2, column=0, columnspan=2, pady=5)
        
        # Results display
        self.ops_result = scrolledtext.ScrolledText(frame, height=12, width=70)
        self.ops_result.grid(row=2, column=0, pady=10)
        
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
                
                result_text += f"{i+1}. {start_dt.strftime('%Y-%m-%d %H:%M')} 至 {end_dt.strftime('%H:%M')}\n"
            
            self.query_result.delete('1.0', tk.END)
            self.query_result.insert(tk.END, result_text)
            self.log(f"查询成功，找到 {num_slots} 个时间段")
            
        except Exception as e:
            messagebox.showerror("错误", f"查询失败: {str(e)}")
            self.log(f"错误: {str(e)}")
            
    def book_facility_action(self):
        """预订设施"""
        try:
            facility_name = self.book_facility.get().strip()
            date_str = self.book_date.get().strip()
            time_str = self.book_time.get().strip()
            duration_hours = float(self.book_duration.get().strip())
            
            # 解析时间
            start_dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
            start_time = int(start_dt.timestamp())
            end_time = start_time + int(duration_hours * 3600)
            
            self.log(f"预订 {facility_name}...")
            
            # 构建请求
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
            
            # 发送请求
            response_data = self.network.send_request(request.get_data())
            if not response_data:
                self.book_result.delete('1.0', tk.END)
                self.book_result.insert(tk.END, "请求超时\n")
                self.log("请求超时")
                return
            
            # 解析响应
            response = ByteBuffer(response_data)
            resp_request_id = response.read_uint32()
            status = response.read_uint8()
            
            if status == MSG_RESPONSE_ERROR:
                error_msg = response.read_string()
                self.book_result.delete('1.0', tk.END)
                self.book_result.insert(tk.END, f"预订失败: {error_msg}\n")
                self.log(f"预订失败: {error_msg}")
                return
            
            # 读取确认ID
            confirmation_id = response.read_uint32()
            result_text = f"✓ 预订成功!\n\n"
            result_text += f"确认ID: {confirmation_id}\n"
            result_text += f"设施: {facility_name}\n"
            result_text += f"时间: {start_dt.strftime('%Y-%m-%d %H:%M')} 至 {datetime.fromtimestamp(end_time).strftime('%H:%M')}\n"
            
            self.book_result.delete('1.0', tk.END)
            self.book_result.insert(tk.END, result_text)
            self.log(f"预订成功，确认ID: {confirmation_id}")
            messagebox.showinfo("成功", f"预订成功！确认ID: {confirmation_id}")
            
        except Exception as e:
            messagebox.showerror("错误", f"预订失败: {str(e)}")
            self.log(f"错误: {str(e)}")
            
    def change_booking(self):
        """修改预订"""
        try:
            confirmation_id = int(self.change_id.get().strip())
            offset_minutes = int(self.change_offset.get().strip())
            
            self.log(f"修改预订 ID {confirmation_id}...")
            
            # 构建请求
            request = ByteBuffer()
            request_id = self.network.get_next_request_id()
            request.write_uint32(request_id)
            request.write_uint8(MSG_CHANGE_BOOKING)
            
            payload = ByteBuffer()
            payload.write_uint32(confirmation_id)
            payload.write_uint32(offset_minutes & 0xFFFFFFFF)
            
            request.write_uint16(len(payload.buffer))
            request.buffer.extend(payload.buffer)
            
            # 发送请求
            response_data = self.network.send_request(request.get_data())
            if not response_data:
                self.change_result.delete('1.0', tk.END)
                self.change_result.insert(tk.END, "请求超时\n")
                self.log("请求超时")
                return
            
            # 解析响应
            response = ByteBuffer(response_data)
            resp_request_id = response.read_uint32()
            status = response.read_uint8()
            
            if status == MSG_RESPONSE_ERROR:
                error_msg = response.read_string()
                self.change_result.delete('1.0', tk.END)
                self.change_result.insert(tk.END, f"修改失败: {error_msg}\n")
                self.log(f"修改失败: {error_msg}")
                return
            
            message = response.read_string()
            self.change_result.delete('1.0', tk.END)
            self.change_result.insert(tk.END, f"✓ {message}\n")
            self.log("预订修改成功")
            messagebox.showinfo("成功", message)
            
        except Exception as e:
            messagebox.showerror("错误", f"修改失败: {str(e)}")
            self.log(f"错误: {str(e)}")
            
    def monitor_facility_action(self):
        """监控设施"""
        facility_name = self.monitor_facility.get().strip()
        duration_seconds = int(self.monitor_duration.get().strip())
        
        # 在新线程中运行监控
        thread = threading.Thread(target=self._monitor_thread, 
                                  args=(facility_name, duration_seconds))
        thread.daemon = True
        thread.start()
        
    def _monitor_thread(self, facility_name: str, duration_seconds: int):
        """监控线程"""
        try:
            self.log(f"开始监控 {facility_name}，时长 {duration_seconds} 秒...")
            
            # 禁用监控按钮
            self.monitor_button.config(state='disabled')
            
            # 构建请求
            request = ByteBuffer()
            request_id = self.network.get_next_request_id()
            request.write_uint32(request_id)
            request.write_uint8(MSG_MONITOR_FACILITY)
            
            payload = ByteBuffer()
            payload.write_string(facility_name)
            payload.write_uint32(duration_seconds)
            
            request.write_uint16(len(payload.buffer))
            request.buffer.extend(payload.buffer)
            
            # 发送请求
            response_data = self.network.send_request(request.get_data())
            if not response_data:
                self.log("监控注册失败：请求超时")
                self.monitor_button.config(state='normal')
                return
            
            # 解析响应
            response = ByteBuffer(response_data)
            resp_request_id = response.read_uint32()
            status = response.read_uint8()
            
            if status == MSG_RESPONSE_ERROR:
                error_msg = response.read_string()
                self.log(f"监控注册失败: {error_msg}")
                self.monitor_button.config(state='normal')
                return
            
            message = response.read_string()
            self.log(f"监控已注册: {message}")
            
            # 显示监控信息
            self.monitor_result.delete('1.0', tk.END)
            self.monitor_result.insert(tk.END, f"正在监控 {facility_name}...\n")
            self.monitor_result.insert(tk.END, f"监控时长: {duration_seconds} 秒\n\n")
            
            # 监听更新
            import time
            start_time = time.time()
            self.network.sock.settimeout(1.0)
            
            while time.time() - start_time < duration_seconds:
                try:
                    update_data, _ = self.network.sock.recvfrom(MAX_BUFFER_SIZE)
                    
                    # 解析更新
                    update = ByteBuffer(update_data)
                    update_status = update.read_uint8()
                    
                    if update_status == MSG_RESPONSE_SUCCESS:
                        update_msg = update.read_string()
                        num_slots = update.read_uint16()
                        
                        result = f"\n*** 更新: {update_msg} ***\n"
                        result += f"可用时间段 ({num_slots}):\n"
                        
                        for i in range(num_slots):
                            start_time_slot = update.read_time()
                            end_time_slot = update.read_time()
                            
                            start_dt = datetime.fromtimestamp(start_time_slot)
                            end_dt = datetime.fromtimestamp(end_time_slot)
                            
                            result += f"  {i+1}. {start_dt.strftime('%Y-%m-%d %H:%M')} 至 {end_dt.strftime('%H:%M')}\n"
                        
                        self.monitor_result.insert(tk.END, result)
                        self.monitor_result.see(tk.END)
                        self.log("收到监控更新")
                    
                except Exception:
                    pass
            
            self.monitor_result.insert(tk.END, "\n监控期结束\n")
            self.log("监控期结束")
            self.network.sock.settimeout(TIMEOUT_SECONDS)
            self.monitor_button.config(state='normal')
            
        except Exception as e:
            self.log(f"监控错误: {str(e)}")
            self.monitor_button.config(state='normal')
            
    def get_last_booking_time(self):
        """获取最后预订时间"""
        try:
            facility_name = self.last_time_facility.get().strip()
            
            self.log(f"查询 {facility_name} 最后预订时间...")
            
            # 构建请求
            request = ByteBuffer()
            request_id = self.network.get_next_request_id()
            request.write_uint32(request_id)
            request.write_uint8(MSG_GET_LAST_BOOKING_TIME)
            
            payload = ByteBuffer()
            payload.write_string(facility_name)
            
            request.write_uint16(len(payload.buffer))
            request.buffer.extend(payload.buffer)
            
            # 发送请求
            response_data = self.network.send_request(request.get_data())
            if not response_data:
                self.ops_result.delete('1.0', tk.END)
                self.ops_result.insert(tk.END, "请求超时\n")
                self.log("请求超时")
                return
            
            # 解析响应
            response = ByteBuffer(response_data)
            resp_request_id = response.read_uint32()
            status = response.read_uint8()
            
            if status == MSG_RESPONSE_ERROR:
                error_msg = response.read_string()
                self.ops_result.delete('1.0', tk.END)
                self.ops_result.insert(tk.END, f"错误: {error_msg}\n")
                self.log(f"错误: {error_msg}")
                return
            
            last_time = response.read_time()
            message = response.read_string()
            
            result_text = f"设施: {facility_name}\n"
            if last_time == 0:
                result_text += f"{message}\n"
            else:
                last_dt = datetime.fromtimestamp(last_time)
                result_text += f"最后预订结束时间: {last_dt.strftime('%Y-%m-%d %H:%M:%S')}\n"
                result_text += f"状态: {message}\n"
            
            self.ops_result.delete('1.0', tk.END)
            self.ops_result.insert(tk.END, result_text)
            self.log("查询成功")
            
        except Exception as e:
            messagebox.showerror("错误", f"查询失败: {str(e)}")
            self.log(f"错误: {str(e)}")
            
    def extend_booking(self):
        """延长预订"""
        try:
            confirmation_id = int(self.extend_id.get().strip())
            minutes_to_extend = int(self.extend_minutes.get().strip())
            
            self.log(f"延长预订 ID {confirmation_id}...")
            
            # 构建请求
            request = ByteBuffer()
            request_id = self.network.get_next_request_id()
            request.write_uint32(request_id)
            request.write_uint8(MSG_EXTEND_BOOKING)
            
            payload = ByteBuffer()
            payload.write_uint32(confirmation_id)
            payload.write_uint32(minutes_to_extend)
            
            request.write_uint16(len(payload.buffer))
            request.buffer.extend(payload.buffer)
            
            # 发送请求
            response_data = self.network.send_request(request.get_data())
            if not response_data:
                self.ops_result.delete('1.0', tk.END)
                self.ops_result.insert(tk.END, "请求超时\n")
                self.log("请求超时")
                return
            
            # 解析响应
            response = ByteBuffer(response_data)
            resp_request_id = response.read_uint32()
            status = response.read_uint8()
            
            if status == MSG_RESPONSE_ERROR:
                error_msg = response.read_string()
                self.ops_result.delete('1.0', tk.END)
                self.ops_result.insert(tk.END, f"延长失败: {error_msg}\n")
                self.log(f"延长失败: {error_msg}")
                return
            
            new_end_time = response.read_time()
            message = response.read_string()
            
            new_end_dt = datetime.fromtimestamp(new_end_time)
            result_text = f"✓ {message}\n"
            result_text += f"新结束时间: {new_end_dt.strftime('%Y-%m-%d %H:%M:%S')}\n"
            
            self.ops_result.delete('1.0', tk.END)
            self.ops_result.insert(tk.END, result_text)
            self.log("延长成功")
            messagebox.showinfo("成功", message)
            
        except Exception as e:
            messagebox.showerror("错误", f"延长失败: {str(e)}")
            self.log(f"错误: {str(e)}")
            
    def run(self):
        """运行GUI主循环"""
        self.log("客户端已启动")
        self.root.mainloop()
        self.network.close()


def main():
    if len(sys.argv) != 3:
        print(f"用法: {sys.argv[0]} <服务器IP> <服务器端口>")
        sys.exit(1)
    
    server_ip = sys.argv[1]
    server_port = int(sys.argv[2])
    
    app = FacilityBookingGUI(server_ip, server_port)
    app.run()


if __name__ == '__main__':
    main()
