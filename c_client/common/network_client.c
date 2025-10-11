#include "network_client.h"
#include "message_types.h"
#include <stdio.h>
#include <string.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>

NetworkClient* network_client_create(const char* server_ip, uint16_t server_port) {
    NetworkClient* client = (NetworkClient*)malloc(sizeof(NetworkClient));
    if (client) {
        client->server_ip = strdup(server_ip);
        client->server_port = server_port;
        client->next_request_id = 1;
        
        // Create UDP socket
        client->sock = socket(AF_INET, SOCK_DGRAM, 0);
        if (client->sock < 0) {
            free((void*)client->server_ip);
            free(client);
            return NULL;
        }

        // Set socket timeout
        struct timeval tv;
        tv.tv_sec = TIMEOUT_SECONDS;
        tv.tv_usec = 0;
        setsockopt(client->sock, SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof(tv));
    }
    return client;
}

void network_client_destroy(NetworkClient* client) {
    if (client) {
        close(client->sock);
        free((void*)client->server_ip);
        free(client);
    }
}

int network_client_send_request(NetworkClient* client, ByteBuffer* request, ByteBuffer* response) {
    struct sockaddr_in server_addr;
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(client->server_port);
    inet_pton(AF_INET, client->server_ip, &server_addr.sin_addr);

    int retries = 0;
    while (retries < MAX_RETRIES) {
        // Send request
        ssize_t sent = sendto(client->sock, byte_buffer_get_data(request), 
                            byte_buffer_get_size(request), 0,
                            (struct sockaddr*)&server_addr, sizeof(server_addr));
        if (sent < 0) {
            return -1;
        }

        // Receive response
        uint8_t buffer[MAX_BUFFER_SIZE];
        socklen_t addr_len = sizeof(server_addr);
        ssize_t received = recvfrom(client->sock, buffer, sizeof(buffer), 0,
                                  (struct sockaddr*)&server_addr, &addr_len);
        
        if (received > 0) {
            // Clear response buffer and copy received data
            byte_buffer_clear(response);
            for (ssize_t i = 0; i < received; i++) {
                byte_buffer_write_uint8(response, buffer[i]);
            }
            return 0;
        }
        
        retries++;
    }

    return -1;
}