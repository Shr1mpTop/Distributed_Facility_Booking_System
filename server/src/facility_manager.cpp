/**
 * Facility Manager Implementation
 */

#include "../include/facility_manager.h"
#include <algorithm>
#include <iostream>

FacilityManager::FacilityManager()
    : next_booking_id(1),
      storage(std::make_unique<JsonStorage>("data"))
{
    // Initialize JSON storage
    if (!storage->initialize())
    {
        std::cerr << "Warning: JSON storage initialization failed, data may not be persisted" << std::endl;
    }
}

void FacilityManager::initialize()
{
    // First try to load data from disk
    load_from_disk();

    // If no facilities were loaded, create default facilities
    if (facilities.empty())
    {
        std::vector<std::string> facility_names = {
            "Conference_Room_A",
            "Conference_Room_B",
            "Lab_101",
            "Lab_102",
            "Auditorium"};

        for (const auto &name : facility_names)
        {
            Facility f;
            f.name = name;
            facilities[name] = f;
        }

        std::cout << "Created " << facilities.size() << " default facilities" << std::endl;
        save_to_disk(); // Save newly created facilities
    }
}

void FacilityManager::save_to_disk()
{
    if (storage)
    {
        storage->save_facilities(facilities);
        storage->save_bookings(bookings_by_id);
    }
}

void FacilityManager::load_from_disk()
{
    if (storage)
    {
        storage->load_facilities(facilities);
        storage->load_bookings(bookings_by_id);

        // Get next booking ID
        next_booking_id = storage->get_next_booking_id();
    }
}

bool FacilityManager::facility_exists(const std::string &name) const
{
    return facilities.find(name) != facilities.end();
}

const Facility &FacilityManager::get_facility(const std::string &name) const
{
    return facilities.at(name);
}

bool FacilityManager::time_ranges_overlap(time_t start1, time_t end1,
                                          time_t start2, time_t end2) const
{
    return (start1 < end2) && (start2 < end1);
}

std::vector<TimeSlot> FacilityManager::get_available_slots(
    const std::string &facility_name,
    const std::vector<uint32_t> &days)
{

    std::vector<TimeSlot> available_slots;

    auto it = facilities.find(facility_name);
    if (it == facilities.end())
    {
        return available_slots;
    }

    const Facility &facility = it->second;

    // For each day, check 9 AM to 6 PM in 1-hour slots
    for (uint32_t day_offset : days)
    {
        time_t day_start = time(nullptr) + (day_offset * 86400);

        struct tm *tm_info = localtime(&day_start);
        tm_info->tm_hour = 9;
        tm_info->tm_min = 0;
        tm_info->tm_sec = 0;
        time_t slot_start = mktime(tm_info);

        for (int hour = 0; hour < 9; hour++)
        {
            time_t slot_end = slot_start + 3600;

            bool is_available = true;
            for (const auto &booking : facility.bookings)
            {
                if (time_ranges_overlap(slot_start, slot_end,
                                        booking.start_time, booking.end_time))
                {
                    is_available = false;
                    break;
                }
            }

            if (is_available)
            {
                available_slots.push_back({slot_start, slot_end});
            }

            slot_start = slot_end;
        }
    }

    return available_slots;
}

uint32_t FacilityManager::create_booking(const std::string &facility_name,
                                         time_t start_time, time_t end_time)
{
    auto it = facilities.find(facility_name);
    if (it == facilities.end())
    {
        return 0;
    }

    // Check for conflicts
    for (const auto &booking : it->second.bookings)
    {
        if (time_ranges_overlap(start_time, end_time,
                                booking.start_time, booking.end_time))
        {
            return 0;
        }
    }

    // Create booking
    Booking new_booking;
    new_booking.booking_id = next_booking_id++;
    new_booking.facility_name = facility_name;
    new_booking.start_time = start_time;
    new_booking.end_time = end_time;

    it->second.bookings.push_back(new_booking);
    bookings_by_id[new_booking.booking_id] = new_booking;

    std::cout << "Created booking ID: " << new_booking.booking_id << std::endl;

    // Save to disk
    save_to_disk();

    return new_booking.booking_id;
}

bool FacilityManager::change_booking(uint32_t booking_id, int32_t offset_minutes)
{
    auto it = bookings_by_id.find(booking_id);
    if (it == bookings_by_id.end())
    {
        return false;
    }

    Booking &booking = it->second;
    time_t new_start = booking.start_time + (offset_minutes * 60);
    time_t new_end = booking.end_time + (offset_minutes * 60);

    // Check for conflicts
    auto fac_it = facilities.find(booking.facility_name);
    for (const auto &other_booking : fac_it->second.bookings)
    {
        if (other_booking.booking_id != booking_id)
        {
            if (time_ranges_overlap(new_start, new_end,
                                    other_booking.start_time, other_booking.end_time))
            {
                return false;
            }
        }
    }

    // Update booking
    booking.start_time = new_start;
    booking.end_time = new_end;

    // Update in facility's booking list
    for (auto &fac_booking : fac_it->second.bookings)
    {
        if (fac_booking.booking_id == booking_id)
        {
            fac_booking.start_time = new_start;
            fac_booking.end_time = new_end;
            break;
        }
    }

    // Save to disk
    save_to_disk();

    return true;
}

bool FacilityManager::extend_booking(uint32_t booking_id, uint32_t minutes_to_extend)
{
    auto it = bookings_by_id.find(booking_id);
    if (it == bookings_by_id.end())
    {
        return false;
    }

    Booking &booking = it->second;
    time_t new_end = booking.end_time + (minutes_to_extend * 60);

    // Check for conflicts
    auto fac_it = facilities.find(booking.facility_name);
    for (const auto &other_booking : fac_it->second.bookings)
    {
        if (other_booking.booking_id != booking_id)
        {
            if (time_ranges_overlap(booking.start_time, new_end,
                                    other_booking.start_time, other_booking.end_time))
            {
                return false;
            }
        }
    }

    // Extend booking
    booking.end_time = new_end;

    // Update in facility's booking list
    for (auto &fac_booking : fac_it->second.bookings)
    {
        if (fac_booking.booking_id == booking_id)
        {
            fac_booking.end_time = new_end;
            break;
        }
    }

    // Save to disk
    save_to_disk();

    return true;
}

bool FacilityManager::booking_exists(uint32_t booking_id) const
{
    return bookings_by_id.find(booking_id) != bookings_by_id.end();
}

const Booking &FacilityManager::get_booking(uint32_t booking_id) const
{
    return bookings_by_id.at(booking_id);
}

time_t FacilityManager::get_last_booking_time(const std::string &facility_name) const
{
    auto it = facilities.find(facility_name);
    if (it == facilities.end())
    {
        return 0;
    }

    time_t last_end_time = 0;
    for (const auto &booking : it->second.bookings)
    {
        if (booking.end_time > last_end_time)
        {
            last_end_time = booking.end_time;
        }
    }

    return last_end_time;
}
