#!/bin/bash

# Distributed Facility Booking System - Server Deployment Script
# 远程服务器自动部署脚本

set -e  # Exit on error

echo "=========================================="
echo "Facility Booking Server Deployment"
echo "=========================================="
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running on server
if [ -z "$1" ]; then
    PORT=8080
else
    PORT=$1
fi

SEMANTIC=${2:-"at-least-once"}

echo -e "${YELLOW}Configuration:${NC}"
echo "  Port: $PORT"
echo "  Semantic: $SEMANTIC"
echo ""

# Step 1: Check dependencies
echo -e "${YELLOW}[1/6] Checking dependencies...${NC}"
if ! command -v g++ &> /dev/null; then
    echo -e "${RED}Error: g++ not found. Please install build tools.${NC}"
    echo "  Ubuntu/Debian: sudo apt install build-essential"
    echo "  CentOS/RHEL: sudo yum groupinstall 'Development Tools'"
    exit 1
fi
if ! command -v make &> /dev/null; then
    echo -e "${RED}Error: make not found.${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Dependencies OK${NC}"
echo ""

# Step 2: Build server
echo -e "${YELLOW}[2/6] Building server...${NC}"
make clean > /dev/null 2>&1 || true
if make; then
    echo -e "${GREEN}✓ Build successful${NC}"
else
    echo -e "${RED}✗ Build failed${NC}"
    echo ""
    echo "Common build issues:"
    echo "  1. Missing g++: sudo apt install g++ (Ubuntu) or sudo yum install gcc-c++ (CentOS)"
    echo "  2. C++17 support: Ensure g++ version >= 7.0"
    echo "  3. Missing nlohmann/json: Already included in server/include/json.hpp"
    echo ""
    echo "Check the error output above for details."
    exit 1
fi
echo ""

# Step 3: Check if server is already running
echo -e "${YELLOW}[3/6] Checking for existing server...${NC}"
if pgrep -f "bin/server" > /dev/null; then
    echo -e "${YELLOW}⚠ Server already running. Stopping...${NC}"
    pkill -f "bin/server" || true
    sleep 2
fi
echo -e "${GREEN}✓ Ready to start${NC}"
echo ""

# Step 4: Create data directory
echo -e "${YELLOW}[4/6] Setting up data directory...${NC}"
mkdir -p data
chmod 755 data
echo -e "${GREEN}✓ Data directory ready${NC}"
echo ""

# Step 5: Configure firewall (optional, requires sudo)
echo -e "${YELLOW}[5/6] Checking firewall...${NC}"
if command -v ufw &> /dev/null; then
    if sudo ufw status 2>/dev/null | grep -q "Status: active"; then
        echo "UFW is active. Attempting to allow port $PORT/udp..."
        if sudo ufw allow $PORT/udp 2>/dev/null; then
            echo -e "${GREEN}✓ Firewall rule added${NC}"
        else
            echo -e "${YELLOW}⚠ Could not add firewall rule (may require manual configuration)${NC}"
        fi
    else
        echo "UFW not active, skipping..."
    fi
elif command -v firewall-cmd &> /dev/null; then
    if sudo firewall-cmd --state 2>/dev/null | grep -q "running"; then
        echo "firewalld is active. Attempting to allow port $PORT/udp..."
        if sudo firewall-cmd --permanent --add-port=$PORT/udp 2>/dev/null && sudo firewall-cmd --reload 2>/dev/null; then
            echo -e "${GREEN}✓ Firewall rule added${NC}"
        else
            echo -e "${YELLOW}⚠ Could not add firewall rule (may require manual configuration)${NC}"
        fi
    else
        echo "firewalld not running, skipping..."
    fi
else
    echo "No firewall detected or configured, skipping..."
fi
echo ""

# Step 6: Create and enable systemd service
echo -e "${YELLOW}[6/6] Creating systemd service...${NC}"
SERVICE_FILE="/etc/systemd/system/facility-server.service"
cat > "$SERVICE_FILE" << EOF
[Unit]
Description=Distributed Facility Booking Server
After=network.target

[Service]
Type=simple
ExecStart=$(pwd)/bin/server $PORT --semantic $SEMANTIC
WorkingDirectory=$(pwd)
Restart=always
RestartSec=5
User=$(whoami)
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable facility-server
sudo systemctl start facility-server

# Wait a moment and check if service started successfully
sleep 2
if sudo systemctl is-active --quiet facility-server; then
    echo -e "${GREEN}✓ Server service started successfully!${NC}"
    echo ""
    echo "=========================================="
    echo -e "${GREEN}Deployment Complete!${NC}"
    echo "=========================================="
    echo ""
    echo "Server Information:"
    echo "  Port: $PORT (UDP)"
    echo "  Semantic: $SEMANTIC"
    echo "  Service: facility-server"
    echo ""
    echo "Service commands:"
    echo "  Status: sudo systemctl status facility-server"
    echo "  Logs: sudo journalctl -u facility-server -f"
    echo "  Stop: sudo systemctl stop facility-server"
    echo "  Restart: sudo systemctl restart facility-server"
    echo "  Disable: sudo systemctl disable facility-server"
    echo ""
    echo "Connect from client:"
    echo "  python3 client/gui/gui_client.py <SERVER_IP> $PORT"
    echo ""
    
    # Show initial log output
    echo "Initial service logs:"
    echo "----------------------------------------"
    sudo journalctl -u facility-server -n 10 --no-pager
    echo "----------------------------------------"
    
else
    echo -e "${RED}✗ Server service failed to start${NC}"
    echo "Check service status:"
    sudo systemctl status facility-server
    exit 1
fi
