/**
 * Facility Booking Client Implementation
 */

#include "facility_client.h"
#include "byte_buffer.h"
#include "message_types.h"
#include <iostream>
#include <iomanip>
#include <sstream>
#include <cstring>
#include <unistd.h>
#include <sys/time.h>

FacilityBookingClient::FacilityBookingClient(const std::string &server_ip, int server_port, double drop_rate)
    : network_client(server_ip, server_port, drop_rate)
{
}

FacilityBookingClient::~FacilityBookingClient()
{
}

bool FacilityBookingClient::query_availability(const std::string &facility_name,
                                               const std::vector<uint32_t> &days,
                                               std::vector<TimeSlot> &available_slots)
{
    // Build request
    ByteBuffer request;
    uint32_t request_id = network_client.get_next_request_id();
    request.write_uint32(request_id);
    request.write_uint8(MSG_QUERY_AVAILABILITY);

    // Build payload
    ByteBuffer payload;
    payload.write_string(facility_name);
    payload.write_uint16(static_cast<uint16_t>(days.size()));
    for (uint32_t day : days)
    {
        payload.write_uint32(day);
    }

    request.write_uint16(static_cast<uint16_t>(payload.size()));
    request.write_bytes(payload.data(), payload.size());

    // Send request
    std::vector<uint8_t> response_data;
    if (!network_client.send_request(request.data(), request.size(), response_data))
    {
        return false;
    }

    // Parse response
    ByteBuffer response(response_data.data(), response_data.size());
    response.read_uint32(); // resp_request_id (not used)
    uint8_t status = response.read_uint8();

    if (status == MSG_RESPONSE_ERROR)
    {
        std::string error_msg = response.read_string();
        std::cerr << "Error: " << error_msg << std::endl;
        return false;
    }

    // Read available time slots
    uint16_t num_slots = response.read_uint16();
    available_slots.clear();

    for (uint16_t i = 0; i < num_slots; ++i)
    {
        TimeSlot slot;
        slot.start_time = response.read_time();
        slot.end_time = response.read_time();
        available_slots.push_back(slot);
    }

    return true;
}

bool FacilityBookingClient::book_facility(const std::string &facility_name,
                                          time_t start_time,
                                          time_t end_time,
                                          uint32_t &confirmation_id)
{
    // Build request
    ByteBuffer request;
    uint32_t request_id = network_client.get_next_request_id();
    request.write_uint32(request_id);
    request.write_uint8(MSG_BOOK_FACILITY);

    ByteBuffer payload;
    payload.write_string(facility_name);
    payload.write_time(start_time);
    payload.write_time(end_time);

    request.write_uint16(static_cast<uint16_t>(payload.size()));
    request.write_bytes(payload.data(), payload.size());

    // Send request
    std::vector<uint8_t> response_data;
    if (!network_client.send_request(request.data(), request.size(), response_data))
    {
        return false;
    }

    // Parse response
    ByteBuffer response(response_data.data(), response_data.size());
    response.read_uint32(); // resp_request_id (not used)
    uint8_t status = response.read_uint8();

    if (status == MSG_RESPONSE_ERROR)
    {
        std::string error_msg = response.read_string();
        std::cerr << "Error: " << error_msg << std::endl;
        return false;
    }

    confirmation_id = response.read_uint32();
    return true;
}

bool FacilityBookingClient::change_booking(uint32_t confirmation_id,
                                           int32_t offset_minutes,
                                           std::string &message)
{
    // Build request
    ByteBuffer request;
    uint32_t request_id = network_client.get_next_request_id();
    request.write_uint32(request_id);
    request.write_uint8(MSG_CHANGE_BOOKING);

    ByteBuffer payload;
    payload.write_uint32(confirmation_id);
    payload.write_uint32(static_cast<uint32_t>(offset_minutes));

    request.write_uint16(static_cast<uint16_t>(payload.size()));
    request.write_bytes(payload.data(), payload.size());

    // Send request
    std::vector<uint8_t> response_data;
    if (!network_client.send_request(request.data(), request.size(), response_data))
    {
        return false;
    }

    // Parse response
    ByteBuffer response(response_data.data(), response_data.size());
    response.read_uint32(); // resp_request_id (not used)
    uint8_t status = response.read_uint8();

    if (status == MSG_RESPONSE_ERROR)
    {
        message = response.read_string();
        std::cerr << "Error: " << message << std::endl;
        return false;
    }

    message = response.read_string();
    return true;
}

bool FacilityBookingClient::monitor_facility(const std::string &facility_name,
                                             uint32_t duration_seconds,
                                             void (*update_callback)(const std::string &, const std::vector<TimeSlot> &))
{
    // Build request
    ByteBuffer request;
    uint32_t request_id = network_client.get_next_request_id();
    request.write_uint32(request_id);
    request.write_uint8(MSG_MONITOR_FACILITY);

    ByteBuffer payload;
    payload.write_string(facility_name);
    payload.write_uint32(duration_seconds);

    request.write_uint16(static_cast<uint16_t>(payload.size()));
    request.write_bytes(payload.data(), payload.size());

    // Send request
    std::vector<uint8_t> response_data;
    if (!network_client.send_request(request.data(), request.size(), response_data))
    {
        return false;
    }

    // Parse response
    ByteBuffer response(response_data.data(), response_data.size());
    response.read_uint32(); // resp_request_id (not used)
    uint8_t status = response.read_uint8();

    if (status == MSG_RESPONSE_ERROR)
    {
        std::string error_msg = response.read_string();
        std::cerr << "Error: " << error_msg << std::endl;
        return false;
    }

    std::string message = response.read_string();
    std::cout << "\n✓ " << message << std::endl;
    std::cout << "Monitoring for " << duration_seconds << " seconds..." << std::endl;
    std::cout << "(Waiting for updates from server...)\n"
              << std::endl;

    // Listen for updates
    // Note: This is a simplified version. In a real implementation,
    // you might want to use a separate thread or async I/O
    time_t start_time = time(nullptr);

    while (time(nullptr) - start_time < duration_seconds)
    {
        std::vector<uint8_t> update_data;
        if (network_client.send_request(nullptr, 0, update_data, 1, 1))
        {
            ByteBuffer update(update_data.data(), update_data.size());
            uint8_t update_status = update.read_uint8();

            if (update_status == MSG_RESPONSE_SUCCESS)
            {
                std::string update_msg = update.read_string();
                uint16_t num_slots = update.read_uint16();

                std::vector<TimeSlot> slots;
                for (uint16_t i = 0; i < num_slots; ++i)
                {
                    TimeSlot slot;
                    slot.start_time = update.read_time();
                    slot.end_time = update.read_time();
                    slots.push_back(slot);
                }

                if (update_callback)
                {
                    update_callback(update_msg, slots);
                }
            }
        }
    }

    std::cout << "Monitoring period ended" << std::endl;
    return true;
}

bool FacilityBookingClient::get_last_booking_time(const std::string &facility_name,
                                                  time_t &last_time,
                                                  std::string &message)
{
    // Build request
    ByteBuffer request;
    uint32_t request_id = network_client.get_next_request_id();
    request.write_uint32(request_id);
    request.write_uint8(MSG_GET_LAST_BOOKING_TIME);

    ByteBuffer payload;
    payload.write_string(facility_name);

    request.write_uint16(static_cast<uint16_t>(payload.size()));
    request.write_bytes(payload.data(), payload.size());

    // Send request
    std::vector<uint8_t> response_data;
    if (!network_client.send_request(request.data(), request.size(), response_data))
    {
        return false;
    }

    // Parse response
    ByteBuffer response(response_data.data(), response_data.size());
    response.read_uint32(); // resp_request_id (not used)
    uint8_t status = response.read_uint8();

    if (status == MSG_RESPONSE_ERROR)
    {
        message = response.read_string();
        std::cerr << "Error: " << message << std::endl;
        return false;
    }

    last_time = response.read_time();
    message = response.read_string();
    return true;
}

bool FacilityBookingClient::extend_booking(uint32_t confirmation_id,
                                           uint32_t minutes_to_extend,
                                           time_t &new_end_time,
                                           std::string &message)
{
    // Build request
    ByteBuffer request;
    uint32_t request_id = network_client.get_next_request_id();
    request.write_uint32(request_id);
    request.write_uint8(MSG_EXTEND_BOOKING);

    ByteBuffer payload;
    payload.write_uint32(confirmation_id);
    payload.write_uint32(minutes_to_extend);

    request.write_uint16(static_cast<uint16_t>(payload.size()));
    request.write_bytes(payload.data(), payload.size());

    // Send request
    std::vector<uint8_t> response_data;
    if (!network_client.send_request(request.data(), request.size(), response_data))
    {
        return false;
    }

    // Parse response
    ByteBuffer response(response_data.data(), response_data.size());
    response.read_uint32(); // resp_request_id (not used)
    uint8_t status = response.read_uint8();

    if (status == MSG_RESPONSE_ERROR)
    {
        message = response.read_string();
        std::cerr << "Error: " << message << std::endl;
        return false;
    }

    new_end_time = response.read_time();
    message = response.read_string();
    return true;
}

// Helper function to format time
static std::string format_time(time_t t)
{
    char buffer[100];
    struct tm *tm_info = localtime(&t);
    strftime(buffer, sizeof(buffer), "%Y-%m-%d %H:%M:%S", tm_info);
    return std::string(buffer);
}

static std::string format_time_short(time_t t)
{
    char buffer[100];
    struct tm *tm_info = localtime(&t);
    strftime(buffer, sizeof(buffer), "%Y-%m-%d %H:%M", tm_info);
    return std::string(buffer);
}

static std::string format_time_only(time_t t)
{
    char buffer[100];
    struct tm *tm_info = localtime(&t);
    strftime(buffer, sizeof(buffer), "%H:%M", tm_info);
    return std::string(buffer);
}

void FacilityBookingClient::run_cli()
{
    std::cout << "============================================================" << std::endl;
    std::cout << "  Distributed Facility Booking System - C++ Client" << std::endl;
    std::cout << "============================================================" << std::endl;
    std::cout << std::endl;

    while (true)
    {
        std::cout << "\n============================================================" << std::endl;
        std::cout << "Menu:" << std::endl;
        std::cout << "  1. Query facility availability" << std::endl;
        std::cout << "  2. Book a facility" << std::endl;
        std::cout << "  3. Change a booking" << std::endl;
        std::cout << "  4. Monitor a facility" << std::endl;
        std::cout << "  5. Get last booking time (idempotent)" << std::endl;
        std::cout << "  6. Extend booking (non-idempotent)" << std::endl;
        std::cout << "  7. Exit" << std::endl;
        std::cout << "============================================================" << std::endl;

        std::cout << "Enter your choice (1-7): ";
        std::string choice;
        std::getline(std::cin, choice);

        try
        {
            if (choice == "1")
            {
                // Query availability
                std::cout << "\n=== Query Facility Availability ===" << std::endl;

                std::cout << "Enter facility name: ";
                std::string facility_name;
                std::getline(std::cin, facility_name);

                std::cout << "Enter days to check (comma-separated, 0=today, 1=tomorrow, etc.): ";
                std::string days_input;
                std::getline(std::cin, days_input);

                std::vector<uint32_t> days;
                std::istringstream iss(days_input);
                std::string day_str;
                while (std::getline(iss, day_str, ','))
                {
                    days.push_back(std::stoul(day_str));
                }

                std::vector<TimeSlot> available_slots;
                if (query_availability(facility_name, days, available_slots))
                {
                    std::cout << "\n"
                              << available_slots.size() << " available time slots found:" << std::endl;
                    for (size_t i = 0; i < available_slots.size(); ++i)
                    {
                        std::cout << "  " << (i + 1) << ". "
                                  << format_time_short(available_slots[i].start_time)
                                  << " to " << format_time_only(available_slots[i].end_time)
                                  << std::endl;
                    }
                }
            }
            else if (choice == "2")
            {
                // Book facility
                std::cout << "\n=== Book Facility ===" << std::endl;

                std::cout << "Enter facility name: ";
                std::string facility_name;
                std::getline(std::cin, facility_name);

                std::cout << "Enter start time:" << std::endl;
                std::cout << "  Date (YYYY-MM-DD): ";
                std::string date_str;
                std::getline(std::cin, date_str);

                std::cout << "  Time (HH:MM): ";
                std::string time_str;
                std::getline(std::cin, time_str);

                // Parse date and time
                struct tm tm_info = {};
                std::string datetime_str = date_str + " " + time_str;
                strptime(datetime_str.c_str(), "%Y-%m-%d %H:%M", &tm_info);
                time_t start_time = mktime(&tm_info);

                std::cout << "Duration in hours: ";
                std::string duration_str;
                std::getline(std::cin, duration_str);
                double duration_hours = std::stod(duration_str);
                time_t end_time = start_time + static_cast<time_t>(duration_hours * 3600);

                uint32_t confirmation_id;
                if (book_facility(facility_name, start_time, end_time, confirmation_id))
                {
                    std::cout << "\n✓ Booking successful!" << std::endl;
                    std::cout << "  Confirmation ID: " << confirmation_id << std::endl;
                    std::cout << "  Facility: " << facility_name << std::endl;
                    std::cout << "  Time: " << format_time_short(start_time)
                              << " to " << format_time_only(end_time) << std::endl;
                }
            }
            else if (choice == "3")
            {
                // Change booking
                std::cout << "\n=== Change Booking ===" << std::endl;

                std::cout << "Enter confirmation ID: ";
                std::string conf_id_str;
                std::getline(std::cin, conf_id_str);
                uint32_t confirmation_id = std::stoul(conf_id_str);

                std::cout << "Enter time offset in minutes (positive or negative): ";
                std::string offset_str;
                std::getline(std::cin, offset_str);
                int32_t offset_minutes = std::stoi(offset_str);

                std::string message;
                if (change_booking(confirmation_id, offset_minutes, message))
                {
                    std::cout << "\n✓ " << message << std::endl;
                }
            }
            else if (choice == "4")
            {
                // Monitor facility
                std::cout << "\n=== Monitor Facility ===" << std::endl;

                std::cout << "Enter facility name to monitor: ";
                std::string facility_name;
                std::getline(std::cin, facility_name);

                std::cout << "Enter monitoring duration in seconds: ";
                std::string duration_str;
                std::getline(std::cin, duration_str);
                uint32_t duration_seconds = std::stoul(duration_str);

                // Define update callback
                auto callback = [](const std::string &msg, const std::vector<TimeSlot> &slots)
                {
                    std::cout << "\n*** UPDATE: " << msg << " ***" << std::endl;
                    std::cout << "Available time slots (" << slots.size() << "):" << std::endl;
                    for (size_t i = 0; i < slots.size(); ++i)
                    {
                        std::cout << "  " << (i + 1) << ". "
                                  << format_time_short(slots[i].start_time)
                                  << " to " << format_time_only(slots[i].end_time)
                                  << std::endl;
                    }
                    std::cout << std::endl;
                };

                monitor_facility(facility_name, duration_seconds, callback);
            }
            else if (choice == "5")
            {
                // Get last booking time
                std::cout << "\n=== Get Last Booking Time ===" << std::endl;

                std::cout << "Enter facility name: ";
                std::string facility_name;
                std::getline(std::cin, facility_name);

                time_t last_time;
                std::string message;
                if (get_last_booking_time(facility_name, last_time, message))
                {
                    if (last_time == 0)
                    {
                        std::cout << "\n"
                                  << message << std::endl;
                    }
                    else
                    {
                        std::cout << "\nLast booking end time: " << format_time(last_time) << std::endl;
                        std::cout << "Status: " << message << std::endl;
                    }
                }
            }
            else if (choice == "6")
            {
                // Extend booking
                std::cout << "\n=== Extend Booking ===" << std::endl;

                std::cout << "Enter confirmation ID: ";
                std::string conf_id_str;
                std::getline(std::cin, conf_id_str);
                uint32_t confirmation_id = std::stoul(conf_id_str);

                std::cout << "Enter minutes to extend: ";
                std::string minutes_str;
                std::getline(std::cin, minutes_str);
                uint32_t minutes_to_extend = std::stoul(minutes_str);

                time_t new_end_time;
                std::string message;
                if (extend_booking(confirmation_id, minutes_to_extend, new_end_time, message))
                {
                    std::cout << "\n✓ " << message << std::endl;
                    std::cout << "  New end time: " << format_time(new_end_time) << std::endl;
                }
            }
            else if (choice == "7")
            {
                std::cout << "\nGoodbye!" << std::endl;
                break;
            }
            else
            {
                std::cout << "Invalid choice, please try again" << std::endl;
            }
        }
        catch (const std::exception &e)
        {
            std::cerr << "Error: " << e.what() << std::endl;
        }
    }
}
