/**
 * Message Types and Constants
 * Defines all message type constants used in communication protocol
 */

#ifndef CPP_CLIENT_MESSAGE_TYPES_H
#define CPP_CLIENT_MESSAGE_TYPES_H

#include <cstdint>

// Message type constants
enum MessageType : uint8_t
{
    MSG_QUERY_AVAILABILITY = 1,
    MSG_BOOK_FACILITY = 2,
    MSG_CHANGE_BOOKING = 3,
    MSG_MONITOR_FACILITY = 4,
    MSG_GET_LAST_BOOKING_TIME = 5,
    MSG_EXTEND_BOOKING = 6,
    MSG_RESPONSE_SUCCESS = 100,
    MSG_RESPONSE_ERROR = 101
};

// Network constants
const int TIMEOUT_SECONDS = 3;
const int MAX_RETRIES = 3;
const size_t MAX_BUFFER_SIZE = 65507;

#endif // CPP_CLIENT_MESSAGE_TYPES_H
