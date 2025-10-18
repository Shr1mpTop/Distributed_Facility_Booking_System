/**
 * Facility Booking Client
 * Main client class for facility booking operations
 */

#ifndef CPP_CLIENT_FACILITY_CLIENT_H
#define CPP_CLIENT_FACILITY_CLIENT_H

#include <string>
#include <vector>
#include <ctime>
#include "network_client.h"

// Time slot structure
struct TimeSlot
{
    time_t start_time;
    time_t end_time;
};

class FacilityBookingClient
{
private:
    NetworkClient network_client;

public:
    FacilityBookingClient(const std::string &server_ip, int server_port, double drop_rate = 0.0);
    ~FacilityBookingClient();

    // Query facility availability
    bool query_availability(const std::string &facility_name,
                            const std::vector<uint32_t> &days,
                            std::vector<TimeSlot> &available_slots);

    // Book a facility
    bool book_facility(const std::string &facility_name,
                       time_t start_time,
                       time_t end_time,
                       uint32_t &confirmation_id);

    // Change booking
    bool change_booking(uint32_t confirmation_id,
                        int32_t offset_minutes,
                        std::string &message);

    // Monitor facility (callback for updates)
    bool monitor_facility(const std::string &facility_name,
                          uint32_t duration_seconds,
                          void (*update_callback)(const std::string &, const std::vector<TimeSlot> &));

    // Get last booking time (idempotent)
    bool get_last_booking_time(const std::string &facility_name,
                               time_t &last_time,
                               std::string &message);

    // Extend booking (non-idempotent)
    bool extend_booking(uint32_t confirmation_id,
                        uint32_t minutes_to_extend,
                        time_t &new_end_time,
                        std::string &message);

    // Run interactive CLI
    void run_cli();
};

#endif // CPP_CLIENT_FACILITY_CLIENT_H
