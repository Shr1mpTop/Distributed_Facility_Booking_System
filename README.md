# 分布式设施预订系统 (模块化版本)

一个基于UDP通信的分布式客户端-服务器应用，用于管理设施预订。系统包含模块化的C++服务器和Python客户端（支持CLI和GUI两种界面）。

## 📁 项目结构

```
Distributed_Facility_Booking_System/
├── server/                      # C++服务器
│   ├── include/                 # 头文件
│   │   ├── message_types.h      # 消息类型定义
│   │   ├── data_structures.h    # 数据结构
│   │   ├── byte_buffer.h        # 序列化/反序列化工具
│   │   ├── facility_manager.h   # 设施管理器
│   │   ├── monitor_manager.h    # 监控管理器
│   │   ├── request_handlers.h   # 请求处理器
│   │   └── udp_server.h         # UDP服务器
│   └── src/                     # 源文件
│       ├── main.cpp
│       ├── byte_buffer.cpp
│       ├── facility_manager.cpp
│       ├── monitor_manager.cpp
│       ├── request_handlers.cpp
│       └── udp_server.cpp
│
├── client/                      # Python客户端
│   ├── common/                  # 公共模块
│   │   ├── __init__.py
│   │   ├── message_types.py     # 消息类型定义
│   │   ├── byte_buffer.py       # 序列化/反序列化工具
│   │   └── network_client.py    # 网络通信模块
│   ├── cli/                     # 命令行界面客户端
│   │   └── cli_client.py
│   └── gui/                     # 图形界面客户端
│       └── gui_client.py        # 使用tkinter的GUI客户端
│
├── bin/                         # 编译后的可执行文件
│   └── server
├── Makefile.new                 # 新的构建文件
└── README_NEW.md               # 本文档
```

## ✨ 主要特性

### 模块化设计

#### C++服务器模块

1. **消息类型 (message_types.h)**: 定义所有通信协议常量
2. **数据结构 (data_structures.h)**: 核心数据结构定义
3. **字节缓冲 (byte_buffer)**: 手动序列化/反序列化
4. **设施管理器 (facility_manager)**: 管理所有设施和预订
5. **监控管理器 (monitor_manager)**: 处理客户端监控注册和通知
6. **请求处理器 (request_handlers)**: 处理各类客户端请求
7. **UDP服务器 (udp_server)**: 网络通信和请求分发

#### Python客户端模块

1. **公共模块 (common/)**: 
   - `message_types.py`: 消息类型常量
   - `byte_buffer.py`: 序列化/反序列化工具类
   - `network_client.py`: UDP通信封装

2. **CLI客户端 (cli/)**: 命令行文本界面
3. **GUI客户端 (gui/)**: 图形用户界面（使用tkinter）

### 核心功能

1. ✅ **查询可用性**: 查看设施的可用时间段
2. ✅ **预订设施**: 预订特定时间段
3. ✅ **修改预订**: 通过时间偏移修改预订
4. ✅ **监控设施**: 实时接收设施可用性更新
5. ✅ **获取最后预订时间** (幂等操作)
6. ✅ **延长预订** (非幂等操作)

### 技术特性

- ✅ 原始UDP套接字通信
- ✅ 手动数据序列化（无RPC/RMI库）
- ✅ 可配置的调用语义（至少一次/至多一次）
- ✅ 自动重试和超时处理
- ✅ 基于回调的监控系统
- ✅ 请求去重（至多一次语义）

## 🔧 系统要求

### 服务器
- **操作系统**: Linux 或 macOS
- **编译器**: g++ 支持 C++17
- **构建工具**: make

### 客户端
- **Python**: 3.6 或更高版本
- **GUI依赖**: tkinter (通常随Python自带)
- **库**: 仅标准库，无需额外依赖

## 🔨 构建系统

### 编译服务器

```bash
# 使用新的Makefile
make -f Makefile.new

# 或者手动编译
g++ -std=c++17 -Wall -Wextra -O2 -I server/include \
    server/src/*.cpp -o bin/server
```

### 清理构建

```bash
make -f Makefile.new clean
```

## 🚀 运行系统

### 1. 启动服务器

#### 至少一次语义（默认）
```bash
./bin/server 8080 --semantic at-least-once
```

#### 至多一次语义
```bash
./bin/server 8080 --semantic at-most-once
```

或使用Makefile:
```bash
make -f Makefile.new run                  # 至少一次
make -f Makefile.new run-at-most-once     # 至多一次
```

### 2. 启动客户端

#### GUI客户端（推荐）

```bash
python3 client/gui/gui_client.py localhost 8080
```

或使用Makefile:
```bash
make -f Makefile.new run-gui
```

#### CLI客户端

```bash
python3 client/cli/cli_client.py localhost 8080
```

或使用Makefile:
```bash
make -f Makefile.new run-cli
```

## 🎨 GUI客户端界面

GUI客户端提供了友好的图形界面，包含以下功能标签页：

### 1. 查询可用性标签页
- 选择设施名称（下拉菜单）
- 输入要查询的天数（逗号分隔）
- 显示所有可用时间段

### 2. 预订设施标签页
- 选择设施名称
- 选择日期和时间
- 输入预订时长
- 获取确认ID

### 3. 修改预订标签页
- 输入确认ID
- 设置时间偏移（分钟）
- 支持正负偏移

### 4. 监控设施标签页
- 选择要监控的设施
- 设置监控时长
- 实时显示更新通知

### 5. 其他操作标签页
- 获取最后预订时间（幂等操作）
- 延长预订（非幂等操作）

### 底部日志区域
- 实时显示所有操作日志
- 带时间戳的消息记录

## 📝 使用示例

### 示例1: 使用GUI查询和预订

1. **启动服务器**:
   ```bash
   ./bin/server 8080 --semantic at-most-once
   ```

2. **启动GUI客户端**:
   ```bash
   python3 client/gui/gui_client.py localhost 8080
   ```

3. **查询可用性**:
   - 切换到"查询可用性"标签
   - 选择"Conference_Room_A"
   - 输入天数: `0,1,2`
   - 点击"查询"按钮

4. **预订设施**:
   - 切换到"预订设施"标签
   - 选择设施
   - 输入日期和时间
   - 点击"预订"按钮
   - 记下确认ID

### 示例2: 监控测试

```bash
# 终端1: 启动服务器
./bin/server 8080

# 终端2: 启动GUI客户端1（监控）
python3 client/gui/gui_client.py localhost 8080
# 在GUI中选择"监控设施"，监控"Lab_101"，120秒

# 终端3: 启动GUI客户端2（预订）
python3 client/gui/gui_client.py localhost 8080
# 在GUI中预订"Lab_101"
# 客户端1应该收到更新通知
```

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

- `1`: 查询可用性
- `2`: 预订设施
- `3`: 修改预订
- `4`: 监控设施
- `5`: 获取最后预订时间
- `6`: 延长预订
- `100`: 成功响应
- `101`: 错误响应

## 🎯 调用语义

### 至少一次 (At-Least-Once)

- **行为**: 服务器处理接收到的每个请求
- **保证**: 请求至少被处理一次（重试时可能多次）
- **适用**: 幂等操作（查询、获取最后预订时间）

### 至多一次 (At-Most-Once)

- **行为**: 服务器缓存响应并检查重复请求
- **保证**: 每个唯一请求最多处理一次
- **实现**: 维护 `(客户端地址, 请求ID)` → `响应` 缓存
- **适用**: 非幂等操作（预订、延长预订）

## 🧪 测试建议

### 功能测试

1. **基本预订流程**:
   - 查询可用性
   - 预订设施
   - 验证确认ID
   - 再次查询验证时间段已被预订

2. **修改预订**:
   - 创建预订
   - 修改预订时间
   - 验证新时间没有冲突

3. **监控功能**:
   - 客户端1注册监控
   - 客户端2进行预订
   - 验证客户端1收到更新

4. **幂等vs非幂等**:
   - 测试"获取最后预订时间"多次调用返回相同结果
   - 测试"延长预订"多次调用会累积效果

### 网络测试

1. **超时重试**: 
   - 临时断开网络
   - 验证客户端自动重试

2. **并发测试**:
   - 多个客户端同时预订同一时间段
   - 验证只有一个成功

## 🌟 与原版本的改进

### 原版本 (单文件)
- ✗ 单个大型源文件
- ✗ 代码耦合度高
- ✗ 难以维护和扩展
- ✗ 仅命令行界面

### 新版本 (模块化)
- ✓ 清晰的模块分离
- ✓ 低耦合高内聚
- ✓ 易于维护和扩展
- ✓ 提供GUI和CLI两种界面
- ✓ 更好的代码组织

## 📚 代码组织优势

1. **可维护性**: 每个模块职责单一，易于理解和修改
2. **可扩展性**: 添加新功能无需修改现有代码
3. **可测试性**: 每个模块可独立测试
4. **可重用性**: 公共模块可在CLI和GUI之间共享
5. **可读性**: 清晰的文件结构和命名

## 🔍 预初始化设施

服务器启动时会初始化以下设施:
- Conference_Room_A
- Conference_Room_B
- Lab_101
- Lab_102
- Auditorium

每个设施的可用时间: 每天 9:00 AM - 6:00 PM，1小时时间段

## ⚠️ 注意事项

1. **端口使用**: 确保选择的端口未被占用
2. **防火墙**: 确保UDP流量被允许
3. **时区**: 服务器和客户端最好在同一时区
4. **GUI依赖**: GUI客户端需要tkinter支持
5. **Python路径**: GUI客户端使用相对导入，确保从正确目录运行

## 🐛 故障排除

### 服务器无法启动
```bash
# 检查端口是否被占用
lsof -i :8080

# 终止占用进程
kill -9 <PID>
```

### 客户端无法连接
```bash
# 验证服务器运行
ps aux | grep server

# 测试网络连接
ping localhost
```

### GUI无法启动
```bash
# 检查tkinter安装
python3 -m tkinter

# 如果缺失，在macOS上:
brew install python-tk
```

## 📄 许可证

本项目为大学教育项目。

## 👨‍💻 开发建议

### 添加新操作

1. 在 `message_types.h` 和 `message_types.py` 中添加新消息类型
2. 在 `request_handlers.h` 中声明处理函数
3. 在 `request_handlers.cpp` 中实现处理逻辑
4. 在 `udp_server.cpp` 的 `process_request` 中添加case
5. 在GUI客户端中添加新的UI组件和处理函数

### 扩展数据结构

1. 在 `data_structures.h` 中定义新结构
2. 在 `facility_manager.h` 中添加相关操作
3. 实现序列化/反序列化逻辑

---

**祝使用愉快！🎉**

如有问题，请查看日志输出或提交Issue。
