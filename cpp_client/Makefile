# Makefile for C++ Facility Booking Client

CXX = clang++
CXXFLAGS = -std=c++17 -Wall -Wextra -g -I./include
LDFLAGS = 

# Directories
SRC_DIR = src
INC_DIR = include
OBJ_DIR = obj
BIN_DIR = bin

# Target executable
TARGET = $(BIN_DIR)/cpp_client

# Source files
SOURCES = $(wildcard $(SRC_DIR)/*.cpp)
OBJECTS = $(patsubst $(SRC_DIR)/%.cpp,$(OBJ_DIR)/%.o,$(SOURCES))

# Default target
all: $(TARGET)

# Create necessary directories
$(OBJ_DIR):
	mkdir -p $(OBJ_DIR)

$(BIN_DIR):
	mkdir -p $(BIN_DIR)

# Link object files to create executable
$(TARGET): $(OBJECTS) | $(BIN_DIR)
	$(CXX) $(OBJECTS) -o $(TARGET) $(LDFLAGS)
	@echo "Build complete: $(TARGET)"

# Compile source files to object files
$(OBJ_DIR)/%.o: $(SRC_DIR)/%.cpp | $(OBJ_DIR)
	$(CXX) $(CXXFLAGS) -c $< -o $@

# Clean build artifacts
clean:
	rm -rf $(OBJ_DIR) $(BIN_DIR)
	@echo "Cleaned build artifacts"

# Run the client (requires SERVER_IP and SERVER_PORT environment variables)
run: $(TARGET)
	@if [ -z "$(SERVER_IP)" ] || [ -z "$(SERVER_PORT)" ]; then \
		echo "Usage: make run SERVER_IP=<ip> SERVER_PORT=<port>"; \
		echo "Example: make run SERVER_IP=127.0.0.1 SERVER_PORT=8080"; \
		exit 1; \
	fi
	$(TARGET) $(SERVER_IP) $(SERVER_PORT)

# Phony targets
.PHONY: all clean run

# Dependencies
$(OBJ_DIR)/byte_buffer.o: $(INC_DIR)/byte_buffer.h
$(OBJ_DIR)/network_client.o: $(INC_DIR)/network_client.h $(INC_DIR)/message_types.h
$(OBJ_DIR)/facility_client.o: $(INC_DIR)/facility_client.h $(INC_DIR)/network_client.h \
                               $(INC_DIR)/byte_buffer.h $(INC_DIR)/message_types.h
$(OBJ_DIR)/main.o: $(INC_DIR)/facility_client.h
