/**
 * Data Structures
 * Core data structures for bookings, facilities, and clients
 */

#ifndef DATA_STRUCTURES_H
#define DATA_STRUCTURES_H

#include <string>
#include <vector>
#include <ctime>
#include <netinet/in.h>

// Booking structure
struct Booking
{
    uint32_t booking_id;
    std::string facility_name;
    time_t start_time;
    time_t end_time;
};

// Time slot for availability
struct TimeSlot
{
    time_t start_time;
    time_t end_time;
};

// Client information for monitoring
struct ClientInfo
{
    sockaddr_in address;
    time_t expiry_time;
};

// Facility structure
struct Facility
{
    std::string name;
    std::vector<Booking> bookings;
};

// Client address for deduplication (used as map key)
struct ClientAddr
{
    uint32_t ip;
    uint16_t port;

    bool operator<(const ClientAddr &other) const
    {
        if (ip != other.ip)
            return ip < other.ip;
        return port < other.port;
    }
};

// Response cache entry for at-most-once semantics
struct CachedResponse
{
    std::vector<uint8_t> response_data;
    time_t timestamp;
};

#endif // DATA_STRUCTURES_H
