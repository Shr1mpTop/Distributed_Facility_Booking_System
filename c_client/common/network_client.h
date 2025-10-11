#ifndef NETWORK_CLIENT_H
#define NETWORK_CLIENT_H

#include <stdint.h>
#include "byte_buffer.h"

typedef struct {
    const char* server_ip;
    uint16_t server_port;
    int sock;
    uint32_t next_request_id;
} NetworkClient;

// Initialize and cleanup
NetworkClient* network_client_create(const char* server_ip, uint16_t server_port);
void network_client_destroy(NetworkClient* client);

// Network operations
int network_client_send_request(NetworkClient* client, ByteBuffer* request, ByteBuffer* response);

#endif // NETWORK_CLIENT_H