/**
 * Request Handlers Implementation
 */

#include "../include/request_handlers.h"
#include "../include/message_types.h"
#include <iostream>

RequestHandlers::RequestHandlers(FacilityManager &fm, MonitorManager &mm)
    : facility_manager(fm), monitor_manager(mm) {}

ByteBuffer RequestHandlers::handle_query_availability(ByteBuffer &request)
{
    std::string facility_name = request.read_string();
    uint16_t num_days = request.read_uint16();

    std::vector<uint32_t> days;
    for (uint16_t i = 0; i < num_days; i++)
    {
        days.push_back(request.read_uint32());
    }

    std::cout << "Query availability for " << facility_name << std::endl;

    ByteBuffer response;

    if (!facility_manager.facility_exists(facility_name))
    {
        response.write_uint8(RESPONSE_ERROR);
        response.write_string("Facility not found");
        return response;
    }

    std::vector<TimeSlot> slots = facility_manager.get_available_slots(facility_name, days);

    response.write_uint8(RESPONSE_SUCCESS);
    response.write_uint16(static_cast<uint16_t>(slots.size()));

    for (const auto &slot : slots)
    {
        response.write_time(slot.start_time);
        response.write_time(slot.end_time);
    }

    return response;
}

ByteBuffer RequestHandlers::handle_book_facility(ByteBuffer &request)
{
    std::string facility_name = request.read_string();
    time_t start_time = request.read_time();
    time_t end_time = request.read_time();

    std::cout << "Book facility: " << facility_name << std::endl;

    ByteBuffer response;

    if (!facility_manager.facility_exists(facility_name))
    {
        response.write_uint8(RESPONSE_ERROR);
        response.write_string("Facility not found");
        return response;
    }

    uint32_t booking_id = facility_manager.create_booking(facility_name, start_time, end_time);

    if (booking_id == 0)
    {
        response.write_uint8(RESPONSE_ERROR);
        response.write_string("Time slot not available");
        return response;
    }

    response.write_uint8(RESPONSE_SUCCESS);
    response.write_uint32(booking_id);

    return response;
}

ByteBuffer RequestHandlers::handle_change_booking(ByteBuffer &request)
{
    uint32_t booking_id = request.read_uint32();
    int32_t offset_minutes = static_cast<int32_t>(request.read_uint32());

    std::cout << "Change booking: " << booking_id << std::endl;

    ByteBuffer response;

    if (!facility_manager.change_booking(booking_id, offset_minutes))
    {
        response.write_uint8(RESPONSE_ERROR);
        response.write_string("Cannot change booking");
        return response;
    }

    response.write_uint8(RESPONSE_SUCCESS);
    response.write_string("Booking updated successfully");

    return response;
}

ByteBuffer RequestHandlers::handle_monitor_facility(ByteBuffer &request,
                                                    const sockaddr_in &client_addr)
{
    std::string facility_name = request.read_string();
    uint32_t duration_seconds = request.read_uint32();

    std::cout << "Monitor facility: " << facility_name << std::endl;

    ByteBuffer response;

    if (!facility_manager.facility_exists(facility_name))
    {
        response.write_uint8(RESPONSE_ERROR);
        response.write_string("Facility not found");
        return response;
    }

    monitor_manager.register_monitor(facility_name, client_addr, duration_seconds);

    response.write_uint8(RESPONSE_SUCCESS);
    response.write_string("Monitoring registered successfully");

    return response;
}

ByteBuffer RequestHandlers::handle_get_last_booking_time(ByteBuffer &request)
{
    std::string facility_name = request.read_string();

    std::cout << "Get last booking time for: " << facility_name << std::endl;

    ByteBuffer response;

    if (!facility_manager.facility_exists(facility_name))
    {
        response.write_uint8(RESPONSE_ERROR);
        response.write_string("Facility not found");
        return response;
    }

    time_t last_end_time = facility_manager.get_last_booking_time(facility_name);

    response.write_uint8(RESPONSE_SUCCESS);
    response.write_time(last_end_time);

    if (last_end_time == 0)
    {
        response.write_string("No bookings found");
    }
    else
    {
        response.write_string("Last booking end time retrieved");
    }

    return response;
}

ByteBuffer RequestHandlers::handle_extend_booking(ByteBuffer &request)
{
    uint32_t booking_id = request.read_uint32();
    uint32_t minutes_to_extend = request.read_uint32();

    std::cout << "Extend booking: " << booking_id << std::endl;

    ByteBuffer response;

    if (!facility_manager.extend_booking(booking_id, minutes_to_extend))
    {
        response.write_uint8(RESPONSE_ERROR);
        response.write_string("Cannot extend booking");
        return response;
    }

    const Booking &booking = facility_manager.get_booking(booking_id);

    response.write_uint8(RESPONSE_SUCCESS);
    response.write_time(booking.end_time);
    response.write_string("Booking extended successfully");

    return response;
}
