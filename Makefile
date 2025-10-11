# Makefile for Distributed Facility Booking System - Modular Version

CXX = g++
CXXFLAGS = -std=c++17 -Wall -Wextra -O2
INCLUDES = -I server/include

SRC_DIR = server/src
SRCS = $(SRC_DIR)/main.cpp \
       $(SRC_DIR)/byte_buffer.cpp \
       $(SRC_DIR)/facility_manager.cpp \
       $(SRC_DIR)/monitor_manager.cpp \
       $(SRC_DIR)/request_handlers.cpp \
       $(SRC_DIR)/udp_server.cpp

TARGET = bin/server

all:
	@mkdir -p bin
	$(CXX) $(CXXFLAGS) $(INCLUDES) $(SRCS) -o $(TARGET)
	@echo "Build complete: $(TARGET)"

debug:
	@mkdir -p bin
	$(CXX) $(CXXFLAGS) -g $(INCLUDES) $(SRCS) -o $(TARGET)
	@echo "Debug build complete: $(TARGET)"

clean:
	rm -rf bin build
	@echo "Cleaned"

run: all
	./$(TARGET) 8080 --semantic at-least-once

run-at-most-once: all
	./$(TARGET) 8080 --semantic at-most-once

run-gui:
	python3 client/gui/gui_client.py localhost 8080

run-cli:
	python3 client/cli/cli_client.py localhost 8080

.PHONY: all debug clean run run-at-most-once run-gui run-cli
