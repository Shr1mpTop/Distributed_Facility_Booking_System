/**
 * Main Server Entry Point
 */

#include "../include/udp_server.h"
#include <iostream>
#include <string>
#include <cstdlib>

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Usage: " << argv[0] << " <port> [--semantic <at-least-once|at-most-once>]" << std::endl;
        return 1;
    }
    
    int port = std::atoi(argv[1]);
    bool use_at_most_once = false;
    
    // Parse semantic argument
    for (int i = 2; i < argc; i++) {
        if (std::string(argv[i]) == "--semantic" && i + 1 < argc) {
            std::string semantic = argv[i + 1];
            if (semantic == "at-most-once") {
                use_at_most_once = true;
            } else if (semantic == "at-least-once") {
                use_at_most_once = false;
            } else {
                std::cerr << "Unknown semantic: " << semantic << std::endl;
                return 1;
            }
        }
    }
    
    UDPServer server(port, use_at_most_once);
    server.start();
    
    return 0;
}
