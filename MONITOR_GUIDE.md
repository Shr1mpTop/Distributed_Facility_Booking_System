# 设施监控功能使用指南

## 功能概述

设施监控功能允许客户端实时监控设施的可用性变化。当监控的设施有任何预订、修改或扩展操作时，服务器会自动推送更新的可用时间槽信息。

## 项目要求实现情况

### ✅ 已实现的功能

1. **客户端注册**
   - 提供设施名称和监控时长
   - 服务器记录客户端的 IP 地址和端口

2. **回调通知**
   - 监控期间，设施有任何预订/修改/扩展操作
   - 服务器通过 UDP 回调向所有注册客户端发送更新后的可用性

3. **超时终止**
   - 监控时长到期后，服务器自动删除客户端记录
   - 停止回调通知

4. **客户端限制**
   - 监控期间禁用其他功能标签页
   - 用户无法输入新请求（符合无需多线程的要求）
   - 但监听线程在后台接收服务器推送的更新

5. **多客户端并发监控**
   - 服务器支持多个客户端同时监控同一设施
   - 所有注册的客户端都会收到更新通知

## 服务器端改进

### 1. 自动通知机制

服务器在以下操作成功后会自动通知所有监控该设施的客户端：

- **预订设施** (BOOK_FACILITY)
- **修改预订** (CHANGE_BOOKING)  
- **扩展预订** (EXTEND_BOOKING)

### 2. 清理机制

- 每次发送通知前自动清理过期的监控注册
- 避免向已过期的客户端发送通知

### 3. ByteBuffer 增强

添加了 `position()` 和 `set_position()` 方法，支持在处理请求时保存和恢复读取位置。

## 客户端使用方法

### 启动客户端

```bash
# 使用默认服务器地址 (8.148.159.175:8080)
python client/gui/gui_client.py

# 或指定服务器地址
python client/gui/gui_client.py <server_ip> <server_port>
```

### 使用监控功能

1. **进入监控标签页**
   - 点击左侧导航栏的 "Monitor" 按钮

2. **配置监控参数**
   - 选择要监控的设施
   - 设置监控时长（秒）
   - 默认 300 秒 (5 分钟)

3. **开始监控**
   - 点击 "Start Monitoring" 按钮
   - 监控期间其他标签页将被禁用
   - 实时更新区域会显示注册成功信息

4. **接收更新**
   - 当监控的设施发生变化时，自动显示更新信息
   - 包括时间戳和完整的可用时间槽列表

5. **停止监控**
   - 点击 "Stop Monitoring" 按钮
   - 或等待监控时长到期自动停止
   - 其他功能将重新启用

## 监控消息格式

### 客户端请求

```
[Request ID (4 bytes)]
[Message Type: MSG_MONITOR_FACILITY (1 byte)]
[Payload Length (2 bytes)]
[Facility Name (string)]
[Duration in seconds (4 bytes)]
```

### 服务器响应

```
[Request ID (4 bytes)]
[Status: SUCCESS/ERROR (1 byte)]
[Message (string)]
```

### 服务器推送更新

```
[Request ID: 0 (4 bytes)]  # 0 表示服务器主动推送
[Status: SUCCESS (1 byte)]
[Message (string)]
[Number of slots (2 bytes)]
[For each slot:]
  [Start time (4 bytes)]
  [End time (4 bytes)]
```

## 测试场景

### 场景 1：单客户端监控

1. 启动客户端A
2. 进入 Monitor 标签页
3. 选择 Conference_Room_A，监控 300 秒
4. 点击 Start Monitoring
5. 切换到另一个客户端B
6. 使用客户端B预订 Conference_Room_A
7. 观察客户端A实时收到可用性更新

### 场景 2：多客户端监控

1. 启动客户端A和客户端B
2. 两个客户端都监控同一设施（如 Lab_101）
3. 使用第三个客户端C进行预订
4. 观察A和B同时收到更新通知

### 场景 3：监控超时

1. 启动客户端，监控设施60秒
2. 等待60秒后
3. 使用另一客户端修改该设施的预订
4. 观察第一个客户端不再收到更新（因为已过期）

## 技术细节

### 线程模型

- **主线程**：GUI 事件循环
- **监听线程**：后台接收服务器推送（daemon线程）
- 使用 `root.after()` 将更新调度到主线程，确保线程安全

### 状态管理

```python
self.monitoring = False  # 监控状态标志
self.monitor_thread = None  # 监听线程引用
```

### 禁用控制

监控期间：
- 其他功能标签页 → DISABLED
- 设施选择下拉框 → DISABLED  
- 监控时长输入框 → DISABLED
- Start Monitoring 按钮 → DISABLED
- Stop Monitoring 按钮 → NORMAL

## 注意事项

1. **监控期间限制**：按照项目要求，监控期间用户无法输入新请求
2. **自动停止**：如果监听线程出错，会自动停止监控并重新启用功能
3. **网络超时**：监听使用1秒超时，定期检查 `monitoring` 标志
4. **线程安全**：所有GUI更新都通过 `root.after()` 在主线程执行

## 故障排查

### 问题：无法收到更新

**检查项**：
- 服务器是否正在运行
- 客户端是否成功注册（查看日志）
- 监控是否已超时
- 网络连接是否正常

### 问题：监控自动停止

**可能原因**：
- 网络连接中断
- 服务器崩溃
- 监听线程异常

**解决方法**：
- 检查日志区域的错误信息
- 重新启动监控

## 开发者信息

### 相关文件

**服务器端**：
- `server/src/udp_server.cpp` - 添加通知触发逻辑
- `server/src/monitor_manager.cpp` - 监控管理和通知发送
- `server/src/byte_buffer.cpp` - 添加位置控制方法

**客户端**：
- `client/gui/gui_client.py` - 集成监控功能
- `client/common/message_types.py` - 消息类型定义
- `client/common/network_client.py` - 网络通信

### 编译和运行

**服务器**：
```bash
cd server
make clean
make
./server 8080 at-most-once 4
```

**客户端**：
```bash
python client/gui/gui_client.py
```
