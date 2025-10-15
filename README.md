# Distributed Facility Booking System

一个高性能的分布式设施预订系统，支持多种客户端（Python、C++、Java），使用UDP协议进行通信。

## 功能特性

- **设施预订管理**：支持会议室、实验室、礼堂等设施的预订
- **并发处理**：多线程服务器，支持高并发请求
- **语义保证**：支持at-least-once和at-most-once语义
- **多语言客户端**：提供Python、C++和Java客户端
- **数据持久化**：使用JSON格式存储预订数据
- **性能监控**：内置性能测试工具

## 系统架构

```
客户端 (Python/C++/Java) ──UDP──> 服务器 (C++)
    │                                   │
    ├── CLI界面                        ├── 设施管理器
    ├── GUI界面                        ├── 请求处理器
    └── 网络通信层                     └── 数据存储层
```

## 核心功能

- **查询可用性**：查询设施在指定日期的可用时间段
- **预订设施**：为设施创建新的预订
- **更改预订**：修改现有预订的时间
- **扩展预订**：延长预订的持续时间
- **获取最后预订时间**：查询设施的最后预订结束时间

## 项目结构

```
├── server/                 # C++ UDP服务器
│   ├── include/           # 头文件
│   ├── src/              # 源代码
│   └── main.cpp          # 服务器入口
├── client/                # Python客户端
│   ├── cli/              # 命令行客户端
│   └── gui/              # GUI客户端
├── cpp_client/            # C++客户端
├── java_client/           # Java GUI客户端
├── performance_test.py    # 性能测试脚本
├── deploy_server.sh      # 服务器部署脚本
└── Makefile              # 构建脚本
```

## 快速开始

### 1. 构建服务器

```bash
# 构建C++服务器
cd server
make

# 或者使用根目录Makefile
make server
```

### 2. 运行服务器

```bash
# 默认端口8080，at-least-once语义
./server/bin/server 8080

# 指定语义和线程数
./server/bin/server 8080 --semantic at-most-once --threads 8
```

### 3. 运行客户端

#### Python客户端
```bash
cd client
python cli/cli_client.py 127.0.0.1 8080
# 或运行GUI客户端
python gui/gui_client.py 127.0.0.1 8080
```

#### C++客户端
```bash
cd cpp_client
make
./bin/cpp_client 127.0.0.1 8080
```

#### Java客户端
```bash
cd java_client
mvn clean package
java -jar target/facility-client-gui.jar 127.0.0.1 8080
```

## 性能测试

运行多线程性能测试：

```bash
python performance_test.py 127.0.0.1 8080 50 100
```

参数说明：服务器IP、端口、线程数、每线程操作数

## 网络协议

使用UDP协议，消息格式：

```
请求:
  [请求ID: 4字节] [消息类型: 1字节] [负载长度: 2字节] [负载: 可变]

响应:
  [请求ID: 4字节] [状态: 1字节] [负载: 可变]
```

## 构建要求

- **服务器**：C++17, CMake或Make
- **Python客户端**：Python 3.6+, 无额外依赖
- **C++客户端**：C++17, Make
- **Java客户端**：Java 11+, Maven 3.6+

## 许可证

本项目采用MIT许可证。