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

    monitors[facility_name].push_back(client_info);

    std::cout << "Registered monitor for " << facility_name << std::endl;
}

void MonitorManager::notify_monitors(const std::string &facility_name,
                                     const std::vector<TimeSlot> &slots,
                                     int sockfd)
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

    // Build notification message
    ByteBuffer notification;
    notification.write_uint32(0);  // request_id = 0 for server-initiated notifications
    notification.write_uint8(RESPONSE_SUCCESS);
    notification.write_string("Facility update: " + facility_name);
    notification.write_uint16(static_cast<uint16_t>(slots.size()));

    for (const auto &slot : slots)
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
            sendto(sockfd, notification.data(), notification.size(), 0,
                   (struct sockaddr *)&client_it->address, sizeof(client_it->address));
            sent_count++;
            ++client_it;
        }
        else
        {
            client_it = clients.erase(client_it);
        }
    }
    
    if (sent_count > 0)
    {
        std::cout << "Sent availability update to " << sent_count 
                  << " monitoring client(s) for " << facility_name << std::endl;
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
