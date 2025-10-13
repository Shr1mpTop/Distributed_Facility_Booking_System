"""
Message Types Constants
Must match server definitions
"""

# Message type constants (must match server/include/message_types.h)
MSG_QUERY_AVAILABILITY = 1
MSG_BOOK_FACILITY = 2
MSG_CHANGE_BOOKING = 3
MSG_MONITOR_FACILITY = 4
MSG_GET_LAST_BOOKING_TIME = 5
MSG_EXTEND_BOOKING = 6

# Legacy/deprecated constants (not supported by server)
MSG_MONITOR_UPDATES = 5  # Same as GET_LAST_BOOKING_TIME
MSG_CANCEL_BOOKING = 4   # Same as MONITOR_FACILITY

# Response message types
MSG_RESPONSE_SUCCESS = 100
MSG_RESPONSE_ERROR = 101

# Booking operation types (for monitor notifications)
OP_BOOK = 1
OP_CHANGE = 2
OP_EXTEND = 3

# Network constants
TIMEOUT_SECONDS = 3
MAX_RETRIES = 3
MAX_BUFFER_SIZE = 65507
