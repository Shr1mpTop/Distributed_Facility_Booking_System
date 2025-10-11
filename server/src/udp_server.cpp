/**
 * UDP Server Implementation
 */

#include "../include/udp_server.h"
#include "../include/message_types.h"
#include <sys/socket.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <iostream>
#include <cstring>

UDPServer::UDPServer(int port, bool at_most_once)
    : port(port), sockfd(-1), use_at_most_once(at_most_once),
      handlers(facility_manager, monitor_manager) {
    facility_manager.initialize();
}

UDPServer::~UDPServer() {
    if (sockfd >= 0) {
        close(sockfd);
    }
}

bool UDPServer::initialize_socket() {
    sockfd = socket(AF_INET, SOCK_DGRAM, 0);
    if (sockfd < 0) {
        std::cerr << "Error creating socket" << std::endl;
        return false;
    }
    
    sockaddr_in server_addr{};
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = INADDR_ANY;
    server_addr.sin_port = htons(port);
    
    if (bind(sockfd, (struct sockaddr*)&server_addr, sizeof(server_addr)) < 0) {
        std::cerr << "Error binding socket" << std::endl;
        close(sockfd);
        return false;
    }
    
    return true;
}

bool UDPServer::check_cache(const ClientAddr& client_key, uint32_t request_id,
                            std::vector<uint8_t>& cached_response) {
    auto client_it = response_cache.find(client_key);
    if (client_it != response_cache.end()) {
        auto request_it = client_it->second.find(request_id);
        if (request_it != client_it->second.end()) {
            cached_response = request_it->second.response_data;
            return true;
        }
    }
    return false;
}

void UDPServer::cache_response(const ClientAddr& client_key, uint32_t request_id,
                               const ByteBuffer& response) {
    CachedResponse cached;
    cached.response_data.assign(response.data(), response.data() + response.size());
    cached.timestamp = time(nullptr);
    
    response_cache[client_key][request_id] = cached;
}

ByteBuffer UDPServer::process_request(ByteBuffer& request, const sockaddr_in& client_addr) {
    uint32_t request_id = request.read_uint32();
    uint8_t message_type = request.read_uint8();
    request.read_uint16();  // payload_length (for protocol consistency)
    
    std::cout << "Processing request ID: " << request_id << ", Type: " << (int)message_type << std::endl;
    
    ByteBuffer response;
    
    try {
        switch (message_type) {
            case QUERY_AVAILABILITY:
                response = handlers.handle_query_availability(request);
                break;
                
            case BOOK_FACILITY:
                response = handlers.handle_book_facility(request);
                break;
                
            case CHANGE_BOOKING:
                response = handlers.handle_change_booking(request);
                break;
                
            case MONITOR_FACILITY:
                response = handlers.handle_monitor_facility(request, client_addr);
                break;
                
            case GET_LAST_BOOKING_TIME:
                response = handlers.handle_get_last_booking_time(request);
                break;
                
            case EXTEND_BOOKING:
                response = handlers.handle_extend_booking(request);
                break;
                
            default:
                response.write_uint8(RESPONSE_ERROR);
                response.write_string("Unknown message type");
                break;
        }
    } catch (const std::exception& e) {
        std::cerr << "Error processing request: " << e.what() << std::endl;
        response = ByteBuffer();
        response.write_uint8(RESPONSE_ERROR);
        response.write_string(std::string("Server error: ") + e.what());
    }
    
    // Prepend response with request_id
    ByteBuffer final_response;
    final_response.write_uint32(request_id);
    final_response.write_bytes(response.data(), response.size());
    
    return final_response;
}

void UDPServer::start() {
    if (!initialize_socket()) {
        return;
    }
    
    std::cout << "Server listening on port " << port << std::endl;
    std::cout << "Invocation semantic: " << (use_at_most_once ? "at-most-once" : "at-least-once") << std::endl;
    
    uint8_t buffer[MAX_BUFFER_SIZE];
    
    while (true) {
        sockaddr_in client_addr{};
        socklen_t client_len = sizeof(client_addr);
        
        ssize_t recv_len = recvfrom(sockfd, buffer, MAX_BUFFER_SIZE, 0,
                                     (struct sockaddr*)&client_addr, &client_len);
        
        if (recv_len < 0) {
            std::cerr << "Error receiving data" << std::endl;
            continue;
        }
        
        std::cout << "\n--- Received " << recv_len << " bytes from "
                  << inet_ntoa(client_addr.sin_addr) << ":" << ntohs(client_addr.sin_port) << std::endl;
        
        try {
            // For at-most-once, check cache first
            if (use_at_most_once) {
                uint32_t request_id;
                std::memcpy(&request_id, buffer, sizeof(request_id));
                request_id = ntohl(request_id);
                
                ClientAddr client_key;
                client_key.ip = client_addr.sin_addr.s_addr;
                client_key.port = client_addr.sin_port;
                
                std::vector<uint8_t> cached_response;
                if (check_cache(client_key, request_id, cached_response)) {
                    std::cout << "Found cached response for request " << request_id << std::endl;
                    
                    sendto(sockfd, cached_response.data(), cached_response.size(), 0,
                           (struct sockaddr*)&client_addr, client_len);
                    continue;
                }
            }
            
            ByteBuffer request(buffer, recv_len);
            ByteBuffer response = process_request(request, client_addr);
            
            // Cache response if using at-most-once
            if (use_at_most_once) {
                uint32_t request_id;
                std::memcpy(&request_id, buffer, sizeof(request_id));
                request_id = ntohl(request_id);
                
                ClientAddr client_key;
                client_key.ip = client_addr.sin_addr.s_addr;
                client_key.port = client_addr.sin_port;
                
                cache_response(client_key, request_id, response);
            }
            
            // Send response
            ssize_t sent = sendto(sockfd, response.data(), response.size(), 0,
                                  (struct sockaddr*)&client_addr, client_len);
            
            if (sent < 0) {
                std::cerr << "Error sending response" << std::endl;
            } else {
                std::cout << "Sent " << sent << " bytes response" << std::endl;
            }
            
        } catch (const std::exception& e) {
            std::cerr << "Error: " << e.what() << std::endl;
        }
    }
}
