#!/bin/bash

# Facility Booking System - Java GUI Client Runner

# Check if arguments are provided
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <server_ip> <server_port>"
    echo "Example: $0 127.0.0.1 8080"
    exit 1
fi

SERVER_IP=$1
SERVER_PORT=$2

# Check if Maven is installed
if ! command -v mvn &> /dev/null; then
    echo "Error: Maven is not installed. Please install Maven first."
    exit 1
fi

# Check if JAR file exists
JAR_FILE="target/facility-client-gui.jar"

if [ ! -f "$JAR_FILE" ]; then
    echo "JAR file not found. Building project..."
    mvn clean package
    
    if [ $? -ne 0 ]; then
        echo "Error: Build failed"
        exit 1
    fi
fi

# Run the application
echo "Starting Facility Booking GUI Client..."
echo "Server: $SERVER_IP:$SERVER_PORT"
java -jar "$JAR_FILE" "$SERVER_IP" "$SERVER_PORT"
