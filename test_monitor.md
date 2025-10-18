# 监控功能测试指南

## 测试目标
验证监控功能是否符合项目要求：
1. ✅ 监控期间客户端被阻塞，不能输入新请求
2. ✅ 支持多个客户端同时监控同一设施
3. ✅ 每次预订/更新时发送完整的整周可用性
4. ✅ 监控到期后自动停止

## 已实现的改进

### 服务器端改进
1. **完整可用性通知**：`notify_monitors` 现在发送：
   - 预订变更信息（操作类型、预订ID、时间）
   - **更新后的整周可用性**（所有可用时段）
   
2. **消息格式**：
   ```
   - request_id (4 bytes)
   - status (1 byte)
   - message (string)
   - operation (1 byte)
   - booking_id (4 bytes)
   - start_time (4 bytes)
   - end_time (4 bytes)
   - [old_start_time, old_end_time for CHANGE/EXTEND]
   - num_slots (2 bytes)
   - [slot_start, slot_end] × num_slots
   ```

### 客户端改进
1. **稳定的监听机制**：
   - 使用 `settimeout(0.5)` 代替非阻塞模式
   - 避免 macOS 的 errno 35 错误
   - 正确处理线程间通信

2. **实时UI更新**：
   - 清除旧的可用性显示
   - 在时间表中标记新的可用时段
   - 显示前5个可用时段的详细信息
   - 强制UI刷新

## 测试步骤

### 测试1：单客户端监控
1. 启动服务器：
   ```bash
   ./bin/server 8080 0  # at-least-once
   ```

2. 启动GUI客户端监控：
   ```bash
   python client/gui/gui_client.py localhost 8080
   ```
   - 切换到 Monitor 标签
   - 选择设施（如 Conference_Room_A）
   - 设置监控时长（如 300 秒）
   - 点击 "Start Monitoring"
   - **验证**：其他标签应被禁用

3. 在另一个终端启动CLI客户端进行预订：
   ```bash
   python client/cli/cli_client.py localhost 8080
   ```
   - 选择 "2. Book a facility"
   - 预订 Conference_Room_A
   
4. **预期结果**：
   - GUI监控窗口立即显示更新
   - 包含预订详细信息
   - 显示更新后的可用性列表
   - 时间表自动刷新

### 测试2：多客户端并发监控
1. 启动服务器（同上）

2. 启动第一个GUI客户端监控 Conference_Room_A

3. 启动第二个GUI客户端监控 Conference_Room_A

4. 启动第三个CLI客户端进行预订操作

5. **预期结果**：
   - 两个GUI客户端同时收到更新通知
   - 显示相同的预订变更信息
   - 显示相同的可用性列表

### 测试3：监控到期
1. 设置较短的监控时长（如 60 秒）
2. 启动监控
3. 等待60秒
4. **预期结果**：
   - 监控自动停止
   - 标签重新启用
   - 可以进行其他操作

### 测试4：不同操作类型
测试三种操作的监控通知：
1. **BOOK**：新建预订
2. **CHANGE**：修改预订（显示旧时间）
3. **EXTEND**：延长预订（显示旧时间）

## 常见问题排查

### 问题1：监控立即停止
- **原因**：Socket 错误未正确处理
- **解决**：已修复 errno 35 (macOS EAGAIN)

### 问题2：更新延迟
- **原因**：UI未强制刷新
- **解决**：添加 `update_idletasks()`

### 问题3：多客户端冲突
- **原因**：端口冲突
- **解决**：UDP自动分配端口，无冲突

### 问题4：Buffer underflow
- **原因**：UDP 包太大被分片
- **解决**：
  - 限制可用时段数量
  - 或切换到TCP（可选）

## 性能考虑
- 每次通知包含完整可用性可能增加消息大小
- 对于繁忙设施，考虑限制返回的时段数量
- UDP最大安全包大小约 1400 字节

## 符合项目要求检查表
- [x] 客户端监控期间被阻塞
- [x] 多客户端并发监控支持
- [x] 发送完整整周可用性
- [x] 监控到期自动清理
- [x] 使用UDP通信
- [x] 回调机制实现
- [x] 线程安全处理
