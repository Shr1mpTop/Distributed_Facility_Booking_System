# 🏢 分布式设施预订系统

[![C++](https://img.shields.io/badge/C++-17-blue.svg)](https://isocpp.org/)
[![Python](https://img.shields.io/badge/Python-3.6+-green.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

一个高性能、多线程的分布式设施预订系统，采用 UDP 通信协议，支持高并发请求处理。

---

## ✨ 核心特性

### 🚀 高性能多线程架构
- **线程池模型**: 生产者-消费者模式，支持高并发
- **可配置线程数**: 根据 CPU 核心数自动调整或手动指定（`--threads N`）
- **读写锁优化**: 查询操作并发执行，修改操作独占访问
- **理论吞吐量**: 800+ 请求/秒（8线程配置）

### ⏰ UTC+8 时区支持
- 统一时区管理，所有时间操作基于 **UTC+8**（中国标准时间）
- 跨平台时区设置（Linux/Windows）
- 确保全球部署时间一致性

### 🔒 双重调用语义
- **至少一次（At-Least-Once）**: 适用于幂等操作（查询、获取信息）
- **至多一次（At-Most-Once）**: 请求去重，适用于非幂等操作（预订、修改）

### 💾 数据持久化
- JSON 格式存储设施和预订数据
- 服务器重启后自动恢复
- 线程安全的磁盘 I/O 操作

### 🖥️ 多客户端支持
- **GUI 客户端**: 基于 tkinter 的图形界面（推荐）
- **CLI 客户端**: 命令行交互界面
- **监控客户端**: 实时监控设施可用性变化

---

## 📋 功能列表

| 功能 | 描述 | 操作类型 |
|-----|------|---------|
| 🔍 查询可用性 | 查看设施的可用时间段 | 幂等 |
| 📅 预订设施 | 预订特定时间段 | 非幂等 |
| ✏️ 修改预订 | 通过时间偏移修改预订 | 非幂等 |
| 👁️ 监控设施 | 实时接收设施可用性更新 | - |
| ⏱️ 获取最后预订时间 | 查询设施最后预订的结束时间 | 幂等 |
| ➕ 延长预订 | 延长现有预订的时长 | 非幂等 |

---

## 🔧 快速开始

### 系统要求

**服务器端**:
- Linux 操作系统（推荐 Ubuntu 18.04+）
- g++ 编译器（支持 C++17）
- make 构建工具

**客户端**:
- Python 3.6+
- tkinter（GUI 客户端需要）

### 安装与运行

```bash
# 1. 克隆仓库
git clone https://github.com/Shr1mpTop/Distributed_Facility_Booking_System.git
cd Distributed_Facility_Booking_System

# 2. 编译服务器（在 Linux 服务器上）
make clean
make

# 3. 启动服务器
./bin/server 8080 --semantic at-least-once --threads 8

# 4. 启动客户端（在本地机器上）
python3 client/gui/gui_client.py <server-ip> 8080
```

### 服务器命令行选项

```bash
./bin/server <port> [OPTIONS]

选项:
  --semantic <at-least-once|at-most-once>  调用语义（默认: at-least-once）
  --threads <N>                            工作线程数（默认: CPU核心数）

示例:
  ./bin/server 8080 --semantic at-most-once --threads 16
```

### 客户端启动

| 客户端 | 命令 | 用途 |
|-------|------|-----|
| **GUI** | `python3 client/gui/gui_client.py <host> <port>` | 图形界面（推荐） |
| **CLI** | `python3 client/cli/cli_client.py <host> <port>` | 命令行界面 |
| **Monitor** | `python3 client/monitor/monitor_client.py <host> <port>` | 实时监控 |

---

## 📊 性能指标

### 并发能力对比

| 指标 | 单线程版本 | 多线程版本(8线程) | 提升 |
|-----|----------|----------------|-----|
| 理论吞吐量 | 100 req/s | 800 req/s | **8x** |
| 查询并发度 | 1 | N个线程 | **Nx** |
| CPU利用率 | 单核 | 多核 | **全核心** |

### 线程配置建议

| 场景 | CPU核心数 | 推荐线程数 | 命令示例 |
|-----|---------|----------|---------|
| 测试环境 | 2-4 | 4 | `--threads 4` |
| 小型生产 | 4-8 | 8 | `--threads 8` |
| 中型生产 | 8-16 | 16 | `--threads 16` |
| 大型生产 | 16+ | CPU核心×2 | `--threads 32` |

---

## 🏗️ 架构设计

### 线程池模型

```
                                    ┌──────────────────┐
                                    │  Worker Thread 1  │
                                    └──────────────────┘
                                             ↑
                                             │
┌─────────────┐         ┌──────────────────────────┐
│   Main      │ ------> │    Task Queue           │
│   Thread    │         │  (Thread-Safe)          │
│  (Receive)  │         └──────────────────────────┘
└─────────────┘                      │
                                     ↓
                                    ┌──────────────────┐
                                    │  Worker Thread N  │
                                    └──────────────────┘
```

**工作流程**:
1. 主线程接收 UDP 请求并加入任务队列
2. 工作线程从队列获取任务并处理
3. 使用读写锁保护共享数据
4. 查询操作可并发，修改操作独占访问

### 线程安全机制

| 数据类型 | 锁类型 | 并发读取 | 独占写入 |
|---------|--------|---------|---------|
| 设施数据 | `std::shared_mutex` | ✅ | ✅ |
| 预订数据 | `std::shared_mutex` | ✅ | ✅ |
| 任务队列 | `std::mutex` | - | ✅ |
| 响应缓存 | `std::mutex` | - | ✅ |
| 统计信息 | `std::atomic` | ✅ | ✅ |

---

## 📁 项目结构

```
Distributed_Facility_Booking_System/
├── server/                      # C++ 多线程服务器
│   ├── include/                 # 头文件
│   │   ├── udp_server.h         # 多线程 UDP 服务器
│   │   ├── facility_manager.h   # 线程安全的设施管理器
│   │   ├── request_handlers.h   # 请求处理器
│   │   └── ...
│   └── src/                     # 源文件
│       ├── main.cpp             # 程序入口（时区设置）
│       ├── udp_server.cpp       # 线程池实现
│       ├── facility_manager.cpp # 读写锁实现
│       └── ...
│
├── client/                      # Python 客户端
│   ├── common/                  # 公共模块
│   ├── cli/                     # 命令行客户端
│   ├── gui/                     # GUI 客户端
│   └── monitor/                 # 监控客户端
│
├── Makefile                     # 构建文件
└── README.md                    # 本文档
```

---

## 🔄 通信协议

### 消息格式

```
┌─────────────────────────────────────┐
│ 请求ID (uint32_t, 网络字节序)      │  4字节
├─────────────────────────────────────┤
│ 消息类型 (uint8_t)                 │  1字节
├─────────────────────────────────────┤
│ 载荷长度 (uint16_t)                │  2字节
├─────────────────────────────────────┤
│ 载荷数据 (可变)                    │  N字节
└─────────────────────────────────────┘
```

### 消息类型

| 类型码 | 名称 | 描述 |
|-------|------|-----|
| `1` | QUERY_AVAILABILITY | 查询可用性 |
| `2` | BOOK_FACILITY | 预订设施 |
| `3` | CHANGE_BOOKING | 修改预订 |
| `4` | MONITOR_FACILITY | 监控设施 |
| `5` | GET_LAST_BOOKING_TIME | 获取最后预订时间 |
| `6` | EXTEND_BOOKING | 延长预订 |
| `100` | RESPONSE_SUCCESS | 成功响应 |
| `101` | RESPONSE_ERROR | 错误响应 |

---

## 🔍 预初始化设施

服务器启动时自动初始化以下设施：

- **Conference_Room_A** - 会议室 A
- **Conference_Room_B** - 会议室 B
- **Lab_101** - 实验室 101
- **Lab_102** - 实验室 102
- **Auditorium** - 礼堂

**可用时间**: 每天 9:00 AM - 6:00 PM（UTC+8），按 1 小时时间段划分

---

## 🐛 故障排除

### 服务器无法启动

```bash
# 检查端口是否被占用
sudo netstat -ulnp | grep 8080

# 终止占用进程
sudo kill -9 <PID>
```

### 客户端无法连接

```bash
# 验证服务器运行
ps aux | grep server

# 检查防火墙
sudo ufw allow 8080/udp

# 测试网络连接
ping <server-ip>
```

### 编译错误

```bash
# 确保在 Linux 环境编译
uname -a

# 检查 g++ 版本（需要 C++17 支持）
g++ --version

# 安装依赖
sudo apt update
sudo apt install build-essential
```

---

## ⚠️ 注意事项

1. **编译环境**: 必须在 Linux 环境编译（使用 Linux 特有网络 API）
2. **GUI 客户端**: 需要在有图形界面的机器上运行（本地 Windows/macOS/Linux）
3. **时区**: 服务器自动设置 UTC+8，无需手动配置
4. **端口**: 确保 UDP 端口未被占用且防火墙已开放
5. **线程数**: 不建议超过 CPU 核心数的 2 倍

---

## 🚀 部署建议

### 开发环境
```bash
./bin/server 8080 --semantic at-least-once --threads 4
```

### 生产环境
```bash
# 后台运行
nohup ./bin/server 8080 --semantic at-most-once --threads 16 > server.log 2>&1 &

# 查看日志
tail -f server.log

# 停止服务器
pkill -f "bin/server"
```

---

## 📄 许可证

本项目为教育项目，遵循 MIT 许可证。

---

## 👨‍💻 作者

- **GitHub**: [Shr1mpTop](https://github.com/Shr1mpTop)
- **项目**: Distributed_Facility_Booking_System

---

**祝使用愉快！🎉**

如有问题，请查看服务器日志或提交 Issue。
