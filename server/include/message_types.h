/**
 * Message Types and Constants
 * Defines all message type constants used in communication protocol
 */

#ifndef MESSAGE_TYPES_H
#define MESSAGE_TYPES_H

#include <cstdint>

// Message type constants
enum MessageType : uint8_t
{
    QUERY_AVAILABILITY = 1,
    BOOK_FACILITY = 2,
    CHANGE_BOOKING = 3,
    MONITOR_FACILITY = 4,
    GET_LAST_BOOKING_TIME = 5,
    EXTEND_BOOKING = 6,
    RESPONSE_SUCCESS = 100,
    RESPONSE_ERROR = 101
};

// Maximum buffer size for UDP packets
const size_t MAX_BUFFER_SIZE = 65507;

#endif // MESSAGE_TYPES_H
