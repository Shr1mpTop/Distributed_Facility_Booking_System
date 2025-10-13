/**
 * Network Client
 * Handles UDP communication with server
 */

#ifndef CPP_CLIENT_NETWORK_CLIENT_H
#define CPP_CLIENT_NETWORK_CLIENT_H

#include <string>
#include <cstdint>
#include <vector>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include "message_types.h"

class NetworkClient
{
private:
    std::string server_ip;
    int server_port;
    int sock_fd;
    struct sockaddr_in server_addr;
    uint32_t next_request_id;

public:
    NetworkClient(const std::string &ip, int port);
    ~NetworkClient();

    // Get next request ID
    uint32_t get_next_request_id();

    // Send request and receive response
    bool send_request(const uint8_t *request_data, size_t request_len,
                      std::vector<uint8_t> &response_data,
                      int retries = MAX_RETRIES,
                      int timeout_sec = TIMEOUT_SECONDS);

    // Close socket
    void close();
};

#endif // CPP_CLIENT_NETWORK_CLIENT_H
