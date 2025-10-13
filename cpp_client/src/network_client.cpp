/**
 * Network Client Implementation
 */

#include "network_client.h"
#include <iostream>
#include <cstring>
#include <unistd.h>
#include <sys/time.h>

NetworkClient::NetworkClient(const std::string &ip, int port)
    : server_ip(ip), server_port(port), next_request_id(1)
{
    // Create UDP socket
    sock_fd = socket(AF_INET, SOCK_DGRAM, 0);
    if (sock_fd < 0)
    {
        throw std::runtime_error("Failed to create socket");
    }

    // Setup server address
    std::memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(server_port);

    if (inet_pton(AF_INET, server_ip.c_str(), &server_addr.sin_addr) <= 0)
    {
        ::close(sock_fd);
        throw std::runtime_error("Invalid server IP address");
    }
}

NetworkClient::~NetworkClient()
{
    close();
}

uint32_t NetworkClient::get_next_request_id()
{
    return next_request_id++;
}

bool NetworkClient::send_request(const uint8_t *request_data, size_t request_len,
                                 std::vector<uint8_t> &response_data,
                                 int retries, int timeout_sec)
{
    // Set socket timeout
    struct timeval tv;
    tv.tv_sec = timeout_sec;
    tv.tv_usec = 0;
    setsockopt(sock_fd, SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof(tv));

    for (int attempt = 0; attempt < retries; ++attempt)
    {
        // Send request
        ssize_t sent = sendto(sock_fd, request_data, request_len, 0,
                              (struct sockaddr *)&server_addr, sizeof(server_addr));

        if (sent < 0)
        {
            std::cerr << "Failed to send request" << std::endl;
            continue;
        }

        // Wait for response
        uint8_t recv_buffer[MAX_BUFFER_SIZE];
        struct sockaddr_in from_addr;
        socklen_t from_len = sizeof(from_addr);

        ssize_t received = recvfrom(sock_fd, recv_buffer, MAX_BUFFER_SIZE, 0,
                                    (struct sockaddr *)&from_addr, &from_len);

        if (received > 0)
        {
            response_data.assign(recv_buffer, recv_buffer + received);
            return true;
        }
        else
        {
            if (attempt < retries - 1)
            {
                std::cout << "Timeout, retrying... (attempt "
                          << (attempt + 2) << "/" << retries << ")" << std::endl;
            }
            else
            {
                std::cerr << "Request timeout after all retries" << std::endl;
            }
        }
    }

    return false;
}

void NetworkClient::close()
{
    if (sock_fd >= 0)
    {
        ::close(sock_fd);
        sock_fd = -1;
    }
}
