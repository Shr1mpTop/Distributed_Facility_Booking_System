# Remote Server Deployment Guide

## 部署概述

本指南将帮助您在远程服务器上部署C++服务器，并从本地客户端连接。

## 架构

```
┌─────────────────┐          Internet/Network          ┌──────────────────┐
│  Local Machine  │◄──────────────────────────────────►│ Remote Server    │
│                 │         UDP Port 8080               │                  │
│  - CLI Client   │                                     │  - C++ Server    │
│  - GUI Client   │                                     │  - Port: 8080    │
│  - Monitor      │                                     │  - Data Storage  │
└─────────────────┘                                     └──────────────────┘
```

## 一、服务器端准备

### 1.1 系统要求

```bash
# 检查操作系统
uname -a

# 确保有以下工具
which g++     # C++ 编译器
which make    # 构建工具
which git     # 版本控制（用于获取代码）
```

**最低要求**:
- **OS**: Linux (Ubuntu 18.04+, CentOS 7+) 或 macOS
- **编译器**: g++ 支持 C++17
- **内存**: 512MB+
- **磁盘**: 100MB+
- **端口**: UDP 8080 (可配置)

### 1.2 安装依赖

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install -y build-essential git
```

#### CentOS/RHEL
```bash
sudo yum groupinstall -y "Development Tools"
sudo yum install -y git
```

#### macOS
```bash
# 安装 Xcode Command Line Tools
xcode-select --install

# 或安装 Homebrew 和 gcc
brew install gcc
```

### 1.3 上传代码到服务器

**方式一：使用 Git (推荐)**
```bash
# 在服务器上
cd ~
git clone https://github.com/Shr1mpTop/Distributed_Facility_Booking_System.git
cd Distributed_Facility_Booking_System
```

**方式二：使用 SCP**
```bash
# 在本地机器上打包
cd /path/to/Distributed_Facility_Booking_System
tar -czf booking_system.tar.gz server/ Makefile

# 上传到服务器
scp booking_system.tar.gz user@your-server-ip:~/

# 在服务器上解压
ssh user@your-server-ip
tar -xzf booking_system.tar.gz
```

**方式三：使用 rsync**
```bash
# 在本地机器上
rsync -avz --exclude='bin/' --exclude='data/' \
    server/ Makefile user@your-server-ip:~/Distributed_Facility_Booking_System/
```

### 1.4 编译服务器

```bash
# 在服务器上
cd ~/Distributed_Facility_Booking_System

# 清理并编译
make clean
make

# 验证编译成功
ls -lh bin/server
```

### 1.5 配置防火墙

#### Ubuntu (UFW)
```bash
# 检查防火墙状态
sudo ufw status

# 允许 UDP 8080
sudo ufw allow 8080/udp

# 如果需要启用防火墙
sudo ufw enable
```

#### CentOS/RHEL (firewalld)
```bash
# 检查防火墙状态
sudo firewall-cmd --state

# 允许 UDP 8080
sudo firewall-cmd --permanent --add-port=8080/udp
sudo firewall-cmd --reload

# 验证规则
sudo firewall-cmd --list-ports
```

#### 云服务器（AWS/阿里云/腾讯云）
除了服务器防火墙，还需要在云服务商控制台配置**安全组**：

1. 登录云服务商控制台
2. 找到安全组设置
3. 添加入站规则：
   - 协议：UDP
   - 端口：8080
   - 源地址：0.0.0.0/0 (所有IP) 或您的客户端IP

### 1.6 启动服务器

#### 基本启动
```bash
# 前台运行（用于测试）
./bin/server 8080 --semantic at-least-once
```

#### 后台运行（推荐）
```bash
# 使用 nohup
nohup ./bin/server 8080 --semantic at-least-once > server.log 2>&1 &

# 查看进程
ps aux | grep server

# 查看日志
tail -f server.log
```

#### 使用 systemd 服务（生产环境推荐）
```bash
# 创建服务文件
sudo nano /etc/systemd/system/booking-server.service
```

添加以下内容：
```ini
[Unit]
Description=Distributed Facility Booking Server
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/home/your-username/Distributed_Facility_Booking_System
ExecStart=/home/your-username/Distributed_Facility_Booking_System/bin/server 8080 --semantic at-least-once
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启用并启动服务：
```bash
# 重载 systemd 配置
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start booking-server

# 设置开机自启
sudo systemctl enable booking-server

# 查看状态
sudo systemctl status booking-server

# 查看日志
sudo journalctl -u booking-server -f
```

### 1.7 验证服务器运行

```bash
# 检查端口是否监听
sudo netstat -ulnp | grep 8080
# 或
sudo ss -ulnp | grep 8080

# 测试本地连接（在服务器上）
echo "test" | nc -u localhost 8080

# 检查进程
ps aux | grep server
```

## 二、本地客户端准备

### 2.1 获取服务器信息

您需要知道：
- **服务器IP地址**: `your-server-ip` (例如: 8.148.159.175)
- **服务器端口**: `8080` (默认)
- **网络可达性**: 确保本地可以访问服务器

### 2.2 测试网络连通性

```bash
# 测试 ICMP (ping)
ping your-server-ip

# 测试 UDP 端口（使用 nc）
# 注意：UDP 测试可能不准确，最好直接用客户端测试
echo "test" | nc -u your-server-ip 8080

# 检查路由
traceroute your-server-ip
```

### 2.3 启动本地客户端

#### ⚠️ 重要提示：GUI 客户端必须在本地运行

GUI 客户端和监控客户端都使用 tkinter，**需要图形界面环境(X11/Wayland)**。
- ✅ **正确**: 在本地机器（有图形界面）上运行 GUI，连接远程服务器
- ❌ **错误**: 在远程无图形界面的服务器上运行 GUI

#### GUI 客户端（推荐用于本地）
```bash
# 在本地机器上（Windows/macOS/Linux with GUI）
cd /path/to/Distributed_Facility_Booking_System

# 启动 GUI 客户端，连接远程服务器
python3 client/gui/gui_client.py your-server-ip 8080

# 例如
python3 client/gui/gui_client.py 8.148.159.175 8080
```

**如果在远程服务器上出现以下错误**:
```
_tkinter.TclError: no display name and no $DISPLAY environment variable
```
这是正常的，因为服务器没有图形界面。请在本地机器上运行 GUI 客户端。

#### CLI 客户端（推荐用于服务器）
```bash
# 可以在本地或服务器上运行
python3 client/cli/cli_client.py your-server-ip 8080

# 如果在服务器上测试，使用 localhost
python3 client/cli/cli_client.py localhost 8080
```

#### 独立监控客户端（仅本地）
```bash
# 需要图形界面，只能在本地运行
python3 client/monitor/monitor_client.py your-server-ip 8080
```

## 三、常见问题排查

### 3.1 连接超时

**问题**: 客户端显示 "Request timeout"

**排查步骤**:
```bash
# 1. 确认服务器运行
ssh user@your-server-ip
ps aux | grep server

# 2. 确认端口监听
sudo netstat -ulnp | grep 8080

# 3. 检查防火墙
sudo ufw status
sudo firewall-cmd --list-ports

# 4. 检查云安全组
# 在云服务商控制台查看

# 5. 测试本地到服务器的 UDP 连接
# 在服务器上运行简单 UDP 服务器
nc -ul 8080

# 在本地测试
echo "test" | nc -u your-server-ip 8080
```

### 3.2 GUI 客户端显示错误

**问题**: 在服务器上运行 GUI 客户端报错
```
_tkinter.TclError: no display name and no $DISPLAY environment variable
```

**原因**: GUI 客户端需要图形界面，远程服务器通常没有

**解决方案**:
1. ✅ **推荐**: 在本地机器上运行 GUI 客户端，连接远程服务器
   ```bash
   # 在本地机器上
   python3 client/gui/gui_client.py 8.148.159.175 8080
   ```

2. 在服务器上使用 CLI 客户端进行测试
   ```bash
   # 在服务器上
   python3 client/cli/cli_client.py localhost 8080
   ```

3. 如果必须在服务器上使用 GUI（不推荐）
   ```bash
   # 使用 X11 转发（性能差，延迟高）
   ssh -X user@your-server-ip
   python3 client/gui/gui_client.py localhost 8080
   ```

### 3.3 服务器崩溃

**问题**: 服务器意外停止

**排查**:
```bash
# 查看日志
tail -100 server.log
# 或
sudo journalctl -u booking-server -n 100

# 检查系统日志
dmesg | tail -50

# 检查资源使用
free -h
df -h
```

### 3.4 数据丢失

**问题**: 服务器重启后预订数据丢失

**解决**:
```bash
# 检查数据目录
ls -la data/
cat data/facilities.json
cat data/bookings.json

# 确保数据目录存在且有写权限
mkdir -p data
chmod 755 data
```

### 3.4 性能问题

**问题**: 响应缓慢

**优化**:
```bash
# 检查系统负载
top
htop

# 检查网络延迟
ping -c 10 your-server-ip

# 增加超时时间（在客户端代码中）
# 修改 client/common/message_types.py
TIMEOUT_SECONDS = 10  # 增加到 10 秒
```

## 四、高级配置

### 4.1 修改端口

如果 8080 端口被占用：

**服务器端**:
```bash
# 使用其他端口启动
./bin/server 9000 --semantic at-least-once
```

**客户端**:
```bash
python3 client/gui/gui_client.py your-server-ip 9000
```

### 4.2 配置日志级别

修改服务器代码以增加详细日志（可选）。

### 4.3 设置数据备份

```bash
# 创建备份脚本
cat > backup_data.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
tar -czf backup_${DATE}.tar.gz data/
# 保留最近7天的备份
find . -name "backup_*.tar.gz" -mtime +7 -delete
EOF

chmod +x backup_data.sh

# 添加到 crontab（每天备份）
crontab -e
# 添加: 0 2 * * * /path/to/backup_data.sh
```

### 4.4 监控服务器健康

```bash
# 创建健康检查脚本
cat > health_check.sh << 'EOF'
#!/bin/bash
if ! pgrep -f "bin/server" > /dev/null; then
    echo "Server is down! Restarting..."
    cd /path/to/Distributed_Facility_Booking_System
    nohup ./bin/server 8080 --semantic at-least-once > server.log 2>&1 &
fi
EOF

chmod +x health_check.sh

# 添加到 crontab（每5分钟检查）
crontab -e
# 添加: */5 * * * * /path/to/health_check.sh
```

## 五、安全建议

### 5.1 限制访问

```bash
# 仅允许特定 IP 访问（如果可能）
sudo ufw allow from your-client-ip to any port 8080 proto udp
```

### 5.2 使用 VPN

如果安全要求高，考虑：
- 使用 VPN 连接到服务器网络
- 不对公网开放端口

### 5.3 添加认证（需要修改代码）

当前实现没有认证机制，生产环境建议添加：
- Token 认证
- IP 白名单
- 请求签名

## 六、部署检查清单

### 服务器端
- [ ] 已安装编译器和构建工具
- [ ] 代码已上传到服务器
- [ ] 服务器编译成功
- [ ] 防火墙规则已配置
- [ ] 云安全组已配置
- [ ] 服务器成功启动
- [ ] 端口正在监听（netstat/ss 验证）
- [ ] 数据目录存在且有权限
- [ ] 日志正常输出

### 客户端
- [ ] Python 3.6+ 已安装
- [ ] 已获取服务器 IP 和端口
- [ ] 网络连通性已测试
- [ ] 客户端可以成功连接

## 七、快速部署命令集合

### 服务器快速部署
```bash
# 一键部署脚本
cd ~
git clone https://github.com/Shr1mpTop/Distributed_Facility_Booking_System.git
cd Distributed_Facility_Booking_System
make clean && make
sudo ufw allow 8080/udp
nohup ./bin/server 8080 --semantic at-least-once > server.log 2>&1 &
tail -f server.log
```

### 客户端快速连接
```bash
# 替换 YOUR_SERVER_IP
python3 client/gui/gui_client.py YOUR_SERVER_IP 8080
```

## 八、示例：完整部署流程

```bash
# === 在远程服务器上 ===
# 1. 连接服务器
ssh user@8.148.159.175

# 2. 安装依赖
sudo apt update && sudo apt install -y build-essential git

# 3. 获取代码
cd ~
git clone https://github.com/Shr1mpTop/Distributed_Facility_Booking_System.git
cd Distributed_Facility_Booking_System

# 4. 编译
make clean && make

# 5. 配置防火墙
sudo ufw allow 8080/udp
sudo ufw status

# 6. 启动服务器
nohup ./bin/server 8080 --semantic at-least-once > server.log 2>&1 &

# 7. 验证运行
ps aux | grep server
sudo netstat -ulnp | grep 8080

# === 在本地机器上 ===
# 8. 启动 GUI 客户端
cd /path/to/Distributed_Facility_Booking_System
python3 client/gui/gui_client.py 8.148.159.175 8080

# 9. 测试功能
# - 查询可用性
# - 预订设施
# - 修改预订
# - 监控设施

# === 验证数据持久化 ===
# 在服务器上停止并重启
pkill -f "bin/server"
nohup ./bin/server 8080 --semantic at-least-once > server.log 2>&1 &

# 在客户端验证数据是否保留
```

## 九、性能参考

在典型配置下（1 vCPU, 1GB RAM）：
- **并发客户端**: 10-50 个
- **响应延迟**: < 100ms (本地网络) / < 500ms (跨国网络)
- **吞吐量**: ~100 requests/second
- **内存占用**: ~10-20MB
- **磁盘占用**: ~100KB (数据文件)

## 十、故障恢复

```bash
# 服务器完全重启后
cd ~/Distributed_Facility_Booking_System
nohup ./bin/server 8080 --semantic at-least-once > server.log 2>&1 &

# 数据会自动从 data/ 目录加载
# 客户端只需重新连接即可
```

## 需要帮助？

如果遇到问题：
1. 检查服务器日志: `tail -f server.log`
2. 检查客户端日志窗口
3. 验证网络连接: `ping` 和 `traceroute`
4. 检查防火墙规则
5. 确认端口没有被其他程序占用

祝部署顺利！🚀
