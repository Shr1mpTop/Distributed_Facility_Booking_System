/**
 * Monitor Manager Implementation
 */

#include "../include/monitor_manager.h"
#include "../include/byte_buffer.h"
#include "../include/message_types.h"
#include <sys/socket.h>
#include <iostream>
#include <algorithm>

MonitorManager::MonitorManager() {}

void MonitorManager::register_monitor(const std::string &facility_name,
                                      const sockaddr_in &client_addr,
                                      uint32_t duration_seconds)
{
    ClientInfo client_info;
    client_info.address = client_addr;
    client_info.expiry_time = time(nullptr) + duration_seconds;

    // Check if this client is already registered for this facility
    auto it = monitors.find(facility_name);
    if (it != monitors.end())
    {
        for (auto &existing_client : it->second)
        {
            if (existing_client.address.sin_addr.s_addr == client_addr.sin_addr.s_addr &&
                existing_client.address.sin_port == client_addr.sin_port)
            {
                // Update expiry time for existing client
                existing_client.expiry_time = client_info.expiry_time;
                std::cout << "Updated monitor registration for " << facility_name << std::endl;
                return;
            }
        }
    }

    // Add new client
    monitors[facility_name].push_back(client_info);

    std::cout << "Registered monitor for " << facility_name << std::endl;
}

void MonitorManager::notify_monitors(const std::string &facility_name,
                                     const BookingChange &change,
                                     int sockfd,
                                     FacilityManager &facility_manager)
{
    // First cleanup expired monitors
    cleanup_expired_monitors();

    auto it = monitors.find(facility_name);
    if (it == monitors.end())
        return;

    time_t now = time(nullptr);
    std::vector<ClientInfo> &clients = it->second;

    if (clients.empty())
        return;

    // Build notification message with booking change info AND updated availability
    ByteBuffer notification;
    notification.write_uint32(0); // request_id = 0 for server-initiated notifications
    notification.write_uint8(RESPONSE_SUCCESS);

    // Build descriptive message
    std::string operation_msg;
    switch (change.operation)
    {
    case OP_BOOK:
        operation_msg = "New booking created";
        break;
    case OP_CHANGE:
        operation_msg = "Booking time changed";
        break;
    case OP_EXTEND:
        operation_msg = "Booking extended";
        break;
    }

    notification.write_string(operation_msg + " for " + facility_name);
    notification.write_uint8(change.operation); // Operation type
    notification.write_uint32(change.booking_id);
    notification.write_time(change.start_time);
    notification.write_time(change.end_time);

    // For change operations, include old times
    if (change.operation == OP_CHANGE || change.operation == OP_EXTEND)
    {
        notification.write_time(change.old_start_time);
        notification.write_time(change.old_end_time);
    }

    // Include updated availability for the next 7 days
    std::vector<uint32_t> days = {0, 1, 2, 3, 4, 5, 6};
    std::vector<TimeSlot> available_slots = facility_manager.get_available_slots(facility_name, days);

    notification.write_uint16(static_cast<uint16_t>(available_slots.size()));
    for (const auto &slot : available_slots)
    {
        notification.write_time(slot.start_time);
        notification.write_time(slot.end_time);
    }

    // Send to all active monitors
    int sent_count = 0;
    auto client_it = clients.begin();
    while (client_it != clients.end())
    {
        if (now < client_it->expiry_time)
        {
            ssize_t sent = sendto(sockfd, notification.data(), notification.size(), 0,
                                  (struct sockaddr *)&client_it->address, sizeof(client_it->address));

            if (sent > 0)
            {
                sent_count++;
            }
            ++client_it;
        }
        else
        {
            client_it = clients.erase(client_it);
        }
    }

    if (sent_count > 0)
    {
        std::cout << "Sent booking change notification to " << sent_count
                  << " monitoring client(s) for " << facility_name
                  << " (Operation: " << operation_msg << ")" << std::endl;
    }
}

void MonitorManager::cleanup_expired_monitors()
{
    time_t now = time(nullptr);

    for (auto &pair : monitors)
    {
        auto &clients = pair.second;
        clients.erase(
            std::remove_if(clients.begin(), clients.end(),
                           [now](const ClientInfo &info)
                           {
                               return now >= info.expiry_time;
                           }),
            clients.end());
    }
}
