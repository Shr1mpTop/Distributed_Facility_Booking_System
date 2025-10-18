#!/usr/bin/env python3
"""
多线程性能测试脚本
测试多客户端并发访问服务器的性能
展示marshalling/unmarshalling性能和多线程处理能力
"""

import sys
import time
import threading
import random
from datetime import datetime
from typing import List, Dict, Tuple
import json
from collections import defaultdict

# 添加client模块到路径
sys.path.insert(0, '/Users/gigg1ty/Documents/GitHub/Distributed_Facility_Booking_System/client')
from common.network_client import NetworkClient
from common.byte_buffer import ByteBuffer
from common.message_types import *


class PerformanceMetrics:
    """性能指标收集器"""
    def __init__(self):
        self.lock = threading.Lock()
        self.request_times: List[float] = []
        self.success_count = 0
        self.error_count = 0
        self.marshalling_times: List[float] = []
        self.unmarshalling_times: List[float] = []
        self.operation_types = defaultdict(int)
        
    def add_request(self, duration: float, success: bool, operation: str, 
                    marshal_time: float, unmarshal_time: float):
        """记录请求性能数据"""
        with self.lock:
            self.request_times.append(duration)
            if success:
                self.success_count += 1
            else:
                self.error_count += 1
            self.marshalling_times.append(marshal_time)
            self.unmarshalling_times.append(unmarshal_time)
            self.operation_types[operation] += 1
    
    def get_statistics(self) -> Dict:
        """计算统计数据"""
        with self.lock:
            total = len(self.request_times)
            if total == 0:
                return {
                    'total_requests': 0,
                    'success_count': 0,
                    'error_count': 0,
                    'success_rate': 0,
                    'avg_time_ms': 0,
                    'min_time_ms': 0,
                    'max_time_ms': 0,
                    'p50_ms': 0,
                    'p90_ms': 0,
                    'p95_ms': 0,
                    'p99_ms': 0,
                    'avg_marshal_ms': 0,
                    'avg_unmarshal_ms': 0,
                    'throughput_rps': 0,
                    'operation_types': {}
                }
            
            sorted_times = sorted(self.request_times)
            avg_time = sum(self.request_times) / total
            min_time = min(self.request_times)
            max_time = max(self.request_times)
            p50 = sorted_times[int(total * 0.5)]
            p90 = sorted_times[int(total * 0.9)]
            p95 = sorted_times[int(total * 0.95)]
            p99 = sorted_times[int(total * 0.99)] if total > 100 else max_time
            
            avg_marshal = sum(self.marshalling_times) / len(self.marshalling_times) if self.marshalling_times else 0
            avg_unmarshal = sum(self.unmarshalling_times) / len(self.unmarshalling_times) if self.unmarshalling_times else 0
            
            return {
                'total_requests': total,
                'success_count': self.success_count,
                'error_count': self.error_count,
                'success_rate': (self.success_count / total * 100) if total > 0 else 0,
                'avg_time_ms': avg_time * 1000,
                'min_time_ms': min_time * 1000,
                'max_time_ms': max_time * 1000,
                'p50_ms': p50 * 1000,
                'p90_ms': p90 * 1000,
                'p95_ms': p95 * 1000,
                'p99_ms': p99 * 1000,
                'avg_marshal_ms': avg_marshal * 1000,
                'avg_unmarshal_ms': avg_unmarshal * 1000,
                'throughput_rps': total / sum(self.request_times) if sum(self.request_times) > 0 else 0,
                'operation_types': dict(self.operation_types)
            }


class FacilityTestClient:
    """测试客户端"""
    def __init__(self, server_ip: str, server_port: int, client_id: int, metrics: PerformanceMetrics, drop_rate: float = 0.0):
        self.server_ip = server_ip
        self.server_port = server_port
        self.client_id = client_id
        self.metrics = metrics
        self.client = NetworkClient(server_ip, server_port, drop_rate)
        self.request_id_counter = 1
    
    def _get_next_request_id(self) -> int:
        """获取下一个请求ID"""
        req_id = self.request_id_counter
        self.request_id_counter += 1
        return req_id
        
    def query_availability(self, facility_name: str, days: List[int]) -> bool:
        """查询设施可用性"""
        # 测量marshalling时间
        marshal_start = time.time()
        
        # 构建请求
        request = ByteBuffer()
        request_id = self._get_next_request_id()
        request.write_uint32(request_id)
        request.write_uint8(MSG_QUERY_AVAILABILITY)
        
        # 构建payload
        payload = ByteBuffer()
        payload.write_string(facility_name)
        payload.write_uint16(len(days))
        for day in days:
            payload.write_uint32(day)
        
        request.write_uint16(len(payload.buffer))
        request.buffer.extend(payload.buffer)
        request_data = request.get_data()
        
        marshal_time = time.time() - marshal_start
        
        # 发送请求并测量总时间
        start_time = time.time()
        response_data = self.client.send_request(request_data)
        duration = time.time() - start_time
        
        # 测量unmarshalling时间
        unmarshal_start = time.time()
        success = False
        if response_data:
            response = ByteBuffer(response_data)
            resp_request_id = response.read_uint32()
            status = response.read_uint8()
            if status == MSG_RESPONSE_SUCCESS:
                success = True
        unmarshal_time = time.time() - unmarshal_start
        
        self.metrics.add_request(duration, success, "QUERY", marshal_time, unmarshal_time)
        return success
    
    def book_facility(self, facility_name: str, start_time: int, end_time: int) -> Tuple[bool, int]:
        """预订设施"""
        marshal_start = time.time()
        
        # 构建请求
        request = ByteBuffer()
        request_id = self._get_next_request_id()
        request.write_uint32(request_id)
        request.write_uint8(MSG_BOOK_FACILITY)
        
        # 构建payload
        payload = ByteBuffer()
        payload.write_string(facility_name)
        payload.write_time(start_time)
        payload.write_time(end_time)
        
        request.write_uint16(len(payload.buffer))
        request.buffer.extend(payload.buffer)
        request_data = request.get_data()
        
        marshal_time = time.time() - marshal_start
        
        start = time.time()
        response_data = self.client.send_request(request_data)
        duration = time.time() - start
        
        unmarshal_start = time.time()
        success = False
        booking_id = 0
        if response_data:
            response = ByteBuffer(response_data)
            resp_request_id = response.read_uint32()
            status = response.read_uint8()
            if status == MSG_RESPONSE_SUCCESS:
                booking_id = response.read_uint32()
                success = True
        unmarshal_time = time.time() - unmarshal_start
        
        self.metrics.add_request(duration, success, "BOOK", marshal_time, unmarshal_time)
        return success, booking_id


def worker_thread(client: FacilityTestClient, operations_per_thread: int, 
                  facilities: List[str], progress_lock: threading.Lock):
    """工作线程：执行随机操作"""
    booking_ids = []
    
    for i in range(operations_per_thread):
        try:
            # 随机选择操作类型（主要是查询和预订）
            operation = random.choice(['query', 'query', 'book'])  # 更多查询操作
            facility = random.choice(facilities)
            
            if operation == 'query':
                # 查询未来0-7天的可用性
                days = [random.randint(0, 7) for _ in range(random.randint(1, 3))]
                client.query_availability(facility, days)
            elif operation == 'book':
                # 预订从现在开始的某个时间
                from datetime import datetime, timedelta
                start_dt = datetime.now() + timedelta(days=random.randint(0, 7), hours=random.randint(0, 23))
                start_time = int(start_dt.timestamp())
                duration = random.randint(1, 4) * 3600  # 1-4小时
                end_time = start_time + duration
                success, booking_id = client.book_facility(facility, start_time, end_time)
                if success and booking_id > 0:
                    booking_ids.append(booking_id)
            
            # 短暂休息以模拟真实场景
            time.sleep(random.uniform(0.001, 0.01))
            
        except Exception as e:
            with progress_lock:
                print(f"[Client {client.client_id}] Error: {e}")


def print_live_stats(metrics: PerformanceMetrics, start_time: float, 
                     total_threads: int, running: threading.Event):
    """实时打印统计信息"""
    while running.is_set():
        time.sleep(1)
        elapsed = time.time() - start_time
        stats = metrics.get_statistics()
        
        if stats:
            print(f"\r实时统计 | 运行时间: {elapsed:.1f}s | "
                  f"请求数: {stats['total_requests']} | "
                  f"成功: {stats['success_count']} | "
                  f"失败: {stats['error_count']} | "
                  f"平均延迟: {stats['avg_time_ms']:.2f}ms | "
                  f"吞吐量: {stats['total_requests']/elapsed:.1f} req/s",
                  end='', flush=True)


def run_performance_test(server_ip: str, server_port: int, 
                         num_threads: int, operations_per_thread: int, drop_rate: float = 0.0):
    """运行性能测试"""
    print("=" * 80)
    print("多线程并发性能测试")
    print("=" * 80)
    print(f"服务器: {server_ip}:{server_port}")
    print(f"并发线程数: {num_threads}")
    print(f"每线程操作数: {operations_per_thread}")
    print(f"总操作数: {num_threads * operations_per_thread}")
    if drop_rate > 0.0:
        print(f"丢包率: {drop_rate}")
    print("=" * 80)
    
    # 测试设施列表（使用服务器中实际存在的设施）
    facilities = ["Conference_Room_A", "Conference_Room_B", "Lab_101", 
                  "Lab_102", "Auditorium"]
    
    # 创建性能指标收集器
    metrics = PerformanceMetrics()
    
    # 创建测试客户端
    clients = [FacilityTestClient(server_ip, server_port, i, metrics, drop_rate) 
               for i in range(num_threads)]
    
    # 启动实时统计线程
    stats_running = threading.Event()
    stats_running.set()
    progress_lock = threading.Lock()
    stats_thread = threading.Thread(target=print_live_stats, 
                                    args=(metrics, time.time(), num_threads, stats_running))
    stats_thread.daemon = True
    stats_thread.start()
    
    print("\n开始测试...")
    start_time = time.time()
    
    # 创建并启动工作线程
    threads = []
    for client in clients:
        thread = threading.Thread(target=worker_thread, 
                                 args=(client, operations_per_thread, facilities, progress_lock))
        threads.append(thread)
        thread.start()
    
    # 等待所有线程完成
    for thread in threads:
        thread.join()
    
    # 停止实时统计
    stats_running.clear()
    time.sleep(0.5)  # 等待统计线程结束
    
    end_time = time.time()
    total_duration = end_time - start_time
    
    # 打印最终统计
    print("\n\n" + "=" * 80)
    print("测试完成 - 最终统计")
    print("=" * 80)
    
    stats = metrics.get_statistics()
    
    print(f"\n📊 基本统计:")
    print(f"   总请求数: {stats['total_requests']}")
    print(f"   成功数: {stats['success_count']} ({stats['success_rate']:.2f}%)")
    print(f"   失败数: {stats['error_count']}")
    print(f"   测试时长: {total_duration:.2f} 秒")
    print(f"   实际吞吐量: {stats['total_requests']/total_duration:.2f} 请求/秒")
    
    print(f"\n⏱️  响应时间 (毫秒):")
    print(f"   平均值: {stats['avg_time_ms']:.2f} ms")
    print(f"   最小值: {stats['min_time_ms']:.2f} ms")
    print(f"   最大值: {stats['max_time_ms']:.2f} ms")
    print(f"   P50: {stats['p50_ms']:.2f} ms")
    print(f"   P90: {stats['p90_ms']:.2f} ms")
    print(f"   P95: {stats['p95_ms']:.2f} ms")
    print(f"   P99: {stats['p99_ms']:.2f} ms")
    
    print(f"\n🔄 Marshalling/Unmarshalling 性能:")
    print(f"   平均 Marshalling 时间: {stats['avg_marshal_ms']:.4f} ms")
    print(f"   平均 Unmarshalling 时间: {stats['avg_unmarshal_ms']:.4f} ms")
    print(f"   序列化开销占比: {(stats['avg_marshal_ms'] + stats['avg_unmarshal_ms']) / stats['avg_time_ms'] * 100:.2f}%")
    
    print(f"\n📈 操作分布:")
    for op, count in stats['operation_types'].items():
        percentage = count / stats['total_requests'] * 100
        print(f"   {op}: {count} ({percentage:.1f}%)")
    
    print("\n" + "=" * 80)
    
    # 保存测试结果
    result_file = f"test_result_python_{num_threads}threads_{int(time.time())}.json"
    with open(result_file, 'w') as f:
        json.dump({
            'test_config': {
                'language': 'Python',
                'server': f"{server_ip}:{server_port}",
                'threads': num_threads,
                'operations_per_thread': operations_per_thread,
                'total_operations': num_threads * operations_per_thread
            },
            'statistics': stats,
            'duration_seconds': total_duration,
            'timestamp': datetime.now().isoformat()
        }, f, indent=2)
    
    print(f"\n✅ 测试结果已保存到: {result_file}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: python performance_test.py <server_ip> <server_port> [num_threads] [ops_per_thread] [--drop-rate rate]")
        print("示例: python performance_test.py 127.0.0.1 8080 50 100 --drop-rate 0.1")
        sys.exit(1)
    
    server_ip = sys.argv[1]
    server_port = int(sys.argv[2])
    num_threads = 50
    ops_per_thread = 100
    drop_rate = 0.0
    
    # Parse additional arguments
    i = 3
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg == "--drop-rate":
            if i + 1 < len(sys.argv):
                try:
                    drop_rate = float(sys.argv[i + 1])
                    if drop_rate < 0.0 or drop_rate > 1.0:
                        print("错误: drop-rate 必须在 0.0 到 1.0 之间")
                        sys.exit(1)
                    i += 2
                except ValueError:
                    print("错误: drop-rate 必须是一个数字")
                    sys.exit(1)
            else:
                print("错误: --drop-rate 需要一个值")
                sys.exit(1)
        elif arg.startswith("--"):
            print(f"未知选项: {arg}")
            print("用法: python performance_test.py <server_ip> <server_port> [num_threads] [ops_per_thread] [--drop-rate rate]")
            sys.exit(1)
        else:
            # Positional arguments
            if i == 3:
                num_threads = int(arg)
            elif i == 4:
                ops_per_thread = int(arg)
            else:
                print("位置参数过多")
                print("用法: python performance_test.py <server_ip> <server_port> [num_threads] [ops_per_thread] [--drop-rate rate]")
                sys.exit(1)
            i += 1
    
    run_performance_test(server_ip, server_port, num_threads, ops_per_thread, drop_rate)
