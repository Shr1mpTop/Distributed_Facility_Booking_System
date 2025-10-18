# 丢包模拟和调用语义演示

本文档说明如何使用丢包模拟功能来演示分布式系统中 At-Least-Once 和 At-Most-Once 调用语义的区别。

## 概述

在分布式系统中，网络不可靠性可能导致消息丢失。为了处理这种情况，系统可以使用不同的调用语义：

- **At-Least-Once**: 客户端重试失败的请求，可能导致操作被执行多次
- **At-Most-Once**: 服务器缓存请求ID，防止重复执行，但可能丢失一些请求

通过模拟丢包，我们可以观察这两种语义在不可靠网络条件下的行为差异。

## 丢包模拟实现

### 客户端丢包模拟
所有客户端都支持 `--drop-rate` 参数来模拟请求丢包：

- **Python CLI**: `python cli_client.py [server_ip] [server_port] [--drop-rate rate]`
- **Python GUI**: `python gui_client.py [server_ip] [server_port] [--drop-rate rate]`
- **Java GUI**: `java FacilityBookingGUI [server_ip] [server_port] [--drop-rate rate]`
- **C++ CLI**: `./cpp_client [server_ip] [server_port] [--drop-rate rate]`

### 服务器丢包模拟
服务器支持 `--drop-rate` 参数来模拟响应丢包：

```bash
./server [port] [--at-most-once] [--threads count] [--drop-rate rate]
```

## 演示场景

### 场景1: At-Least-Once 语义演示

1. 启动服务器（默认 At-Least-Once）：
   ```bash
   ./server 8080 --drop-rate 0.3
   ```

2. 启动客户端并设置丢包率：
   ```bash
   python cli_client.py 127.0.0.1 8080 --drop-rate 0.2
   ```

3. 执行非幂等操作（如预订设施）：
   - 选择选项 2 (Book a facility)
   - 观察重试行为和可能的重复预订

### 场景2: At-Most-Once 语义演示

1. 启动服务器（启用 At-Most-Once）：
   ```bash
   ./server 8080 --at-most-once --drop-rate 0.3
   ```

2. 启动客户端：
   ```bash
   python cli_client.py 127.0.0.1 8080 --drop-rate 0.2
   ```

3. 执行相同操作：
   - 观察服务器如何防止重复执行
   - 比较与 At-Least-Once 的行为差异

## 观察到的行为

### At-Least-Once 语义
- 客户端重试失败的请求
- 服务器不缓存请求ID
- 可能导致重复操作执行
- 示例输出：
  ```
  [DROP] Request dropped (attempt 1/3)
  Timeout, retrying... (attempt 2/3)
  Booking successful (but may have been executed multiple times)
  ```

### At-Most-Once 语义
- 服务器缓存已处理的请求ID
- 重复请求被拒绝
- 防止重复操作，但可能丢失一些请求
- 示例输出：
  ```
  [DROP] Request dropped (attempt 1/3)
  Timeout, retrying... (attempt 2/3)
  Duplicate request detected - operation already performed
  ```

## 参数说明

- `--drop-rate rate`: 丢包率，范围 0.0-1.0
  - 0.0: 无丢包（默认）
  - 0.1: 10% 丢包率
  - 0.3: 30% 丢包率（推荐用于演示）
  - 1.0: 100% 丢包率

## 推荐测试配置

### 基本演示
- 服务器丢包率: 0.3
- 客户端丢包率: 0.2
- 操作: 预订设施（非幂等操作）

### 压力测试
- 服务器丢包率: 0.5
- 客户端丢包率: 0.5
- 使用性能测试脚本: `python performance_test.py --drop-rate 0.3`

## 故障排除

1. **编译错误**: 确保所有依赖都已安装
2. **连接失败**: 检查服务器是否正在运行
3. **无丢包效果**: 确认参数格式正确（--drop-rate 0.3）
4. **性能问题**: 高丢包率可能导致延迟增加

## 扩展阅读

- 查看 `MONITOR_IMPLEMENTATION.md` 了解监控系统
- 查看 `README.md` 了解项目架构
- 查看 `test_monitor.md` 了解测试方法</content>
<parameter name="filePath">/Users/gigg1ty/Documents/GitHub/Distributed_Facility_Booking_System/PACKET_DROP_SIMULATION.md