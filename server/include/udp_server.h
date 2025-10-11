/**
 * UDP Server
 * Manages network communication and request processing
 */

#ifndef UDP_SERVER_H
#define UDP_SERVER_H

#include "facility_manager.h"
#include "monitor_manager.h"
#include "request_handlers.h"
#include "data_structures.h"
#include <map>

class UDPServer
{
private:
    int port;
    int sockfd;
    bool use_at_most_once;

    FacilityManager facility_manager;
    MonitorManager monitor_manager;
    RequestHandlers handlers;

    // Response cache for at-most-once semantics
    std::map<ClientAddr, std::map<uint32_t, CachedResponse>> response_cache;

public:
    UDPServer(int port, bool at_most_once);
    ~UDPServer();

    // Start the server
    void start();

private:
    bool initialize_socket();
    ByteBuffer process_request(ByteBuffer &request, const sockaddr_in &client_addr);
    bool check_cache(const ClientAddr &client_key, uint32_t request_id,
                     std::vector<uint8_t> &cached_response);
    void cache_response(const ClientAddr &client_key, uint32_t request_id,
                        const ByteBuffer &response);
};

#endif // UDP_SERVER_H
