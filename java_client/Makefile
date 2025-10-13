# Makefile for Java GUI Client

.PHONY: all build clean run help

# Default target
all: build

# Build the project
build:
	@echo "Building Java GUI Client..."
	mvn clean package

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	mvn clean

# Run the application (requires SERVER_IP and SERVER_PORT environment variables)
run:
	@if [ -z "$(SERVER_IP)" ] || [ -z "$(SERVER_PORT)" ]; then \
		echo "Usage: make run SERVER_IP=<ip> SERVER_PORT=<port>"; \
		echo "Example: make run SERVER_IP=127.0.0.1 SERVER_PORT=8080"; \
		exit 1; \
	fi
	@echo "Starting Java GUI Client..."
	java -jar target/facility-client-gui.jar $(SERVER_IP) $(SERVER_PORT)

# Install dependencies only
install:
	@echo "Installing dependencies..."
	mvn dependency:resolve

# Show help
help:
	@echo "Available targets:"
	@echo "  make build              - Build the project"
	@echo "  make clean              - Clean build artifacts"
	@echo "  make run SERVER_IP=<ip> SERVER_PORT=<port> - Run the application"
	@echo "  make install            - Install dependencies"
	@echo "  make help               - Show this help message"
	@echo ""
	@echo "Example:"
	@echo "  make build"
	@echo "  make run SERVER_IP=127.0.0.1 SERVER_PORT=8080"
