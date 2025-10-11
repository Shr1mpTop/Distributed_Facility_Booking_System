/**
 * Facility Manager
 * Manages all facilities and their bookings
 */

#ifndef FACILITY_MANAGER_H
#define FACILITY_MANAGER_H

#include "data_structures.h"
#include <map>
#include <string>
#include <vector>

class FacilityManager
{
private:
    std::map<std::string, Facility> facilities;
    std::map<uint32_t, Booking> bookings_by_id;
    uint32_t next_booking_id;

public:
    FacilityManager();

    // Initialize facilities
    void initialize();

    // Facility queries
    bool facility_exists(const std::string &name) const;
    const Facility &get_facility(const std::string &name) const;

    // Booking operations
    std::vector<TimeSlot> get_available_slots(const std::string &facility_name,
                                              const std::vector<uint32_t> &days);
    uint32_t create_booking(const std::string &facility_name,
                            time_t start_time, time_t end_time);
    bool change_booking(uint32_t booking_id, int32_t offset_minutes);
    bool extend_booking(uint32_t booking_id, uint32_t minutes_to_extend);

    // Booking queries
    bool booking_exists(uint32_t booking_id) const;
    const Booking &get_booking(uint32_t booking_id) const;
    time_t get_last_booking_time(const std::string &facility_name) const;

private:
    bool time_ranges_overlap(time_t start1, time_t end1, time_t start2, time_t end2) const;
};

#endif // FACILITY_MANAGER_H
