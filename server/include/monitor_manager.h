/**
 * Monitor Manager
 * Manages client monitoring registrations and notifications
 */

#ifndef MONITOR_MANAGER_H
#define MONITOR_MANAGER_H

#include "data_structures.h"
#include <map>
#include <string>
#include <vector>

class MonitorManager
{
private:
    std::map<std::string, std::vector<ClientInfo>> monitors;

public:
    MonitorManager();

    // Register a client for monitoring
    void register_monitor(const std::string &facility_name,
                          const sockaddr_in &client_addr,
                          uint32_t duration_seconds);

    // Notify all monitors for a facility about a booking change
    void notify_monitors(const std::string &facility_name,
                         const BookingChange &change,
                         int sockfd);

    // Clean up expired monitor registrations
    void cleanup_expired_monitors();
};

#endif // MONITOR_MANAGER_H
