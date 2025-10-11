# Compiler and flags
CC = gcc
CFLAGS = -Wall -Wextra -g
INCLUDES = -I./common
LIBS = -lpthread

# Directories
COMMON_DIR = common
CLI_DIR = cli
GUI_DIR = gui
MONITOR_DIR = monitor
BUILD_DIR = build

# Source files
COMMON_SRCS = $(wildcard $(COMMON_DIR)/*.c)
CLI_SRCS = $(wildcard $(CLI_DIR)/*.c)
GUI_SRCS = $(wildcard $(GUI_DIR)/*.c)
MONITOR_SRCS = $(wildcard $(MONITOR_DIR)/*.c)

# Object files
COMMON_OBJS = $(COMMON_SRCS:%.c=$(BUILD_DIR)/%.o)
CLI_OBJS = $(CLI_SRCS:%.c=$(BUILD_DIR)/%.o)
GUI_OBJS = $(GUI_SRCS:%.c=$(BUILD_DIR)/%.o)
MONITOR_OBJS = $(MONITOR_SRCS:%.c=$(BUILD_DIR)/%.o)

# Targets
all: directories cli_client gui_client monitor_client

directories:
	mkdir -p $(BUILD_DIR)/$(COMMON_DIR)
	mkdir -p $(BUILD_DIR)/$(CLI_DIR)
	mkdir -p $(BUILD_DIR)/$(GUI_DIR)
	mkdir -p $(BUILD_DIR)/$(MONITOR_DIR)

cli_client: $(COMMON_OBJS) $(CLI_OBJS)
	$(CC) $(CFLAGS) $^ -o $(BUILD_DIR)/$@ $(LIBS)

gui_client: $(COMMON_OBJS) $(GUI_OBJS)
	$(CC) $(CFLAGS) $^ -o $(BUILD_DIR)/$@ $(LIBS)

monitor_client: $(COMMON_OBJS) $(MONITOR_OBJS)
	$(CC) $(CFLAGS) $^ -o $(BUILD_DIR)/$@ $(LIBS)

$(BUILD_DIR)/%.o: %.c
	$(CC) $(CFLAGS) $(INCLUDES) -c $< -o $@

clean:
	rm -rf $(BUILD_DIR)

.PHONY: all directories clean