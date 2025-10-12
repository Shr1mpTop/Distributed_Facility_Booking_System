/**
 * Main Server Entry Point
 */

#include "../include/udp_server.h"
#include <iostream>
#include <string>
#include <cstdlib>
#include <ctime>

int main(int argc, char* argv[]) {
    // Set timezone to UTC+8 (China Standard Time)
    // This ensures all time operations use UTC+8
#ifdef _WIN32
    _putenv("TZ=CST-8");
#else
    setenv("TZ", "Asia/Shanghai", 1);
#endif
    tzset();
    
    std::cout << "Server timezone set to UTC+8 (CST)" << std::endl;
    
    if (argc < 2) {
        std::cerr << "Usage: " << argv[0] << " <port> [--semantic <at-least-once|at-most-once>] [--threads <count>]" << std::endl;
        return 1;
    }
    
    int port = std::atoi(argv[1]);
    bool use_at_most_once = false;
    size_t thread_count = std::thread::hardware_concurrency();  // Default to CPU core count
    
    if (thread_count == 0) {
        thread_count = 4;  // Fallback if detection fails
    }
    
    // Parse command line arguments
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
            i++;  // Skip next argument
        } else if (std::string(argv[i]) == "--threads" && i + 1 < argc) {
            thread_count = std::atoi(argv[i + 1]);
            if (thread_count == 0) {
                std::cerr << "Invalid thread count, using default" << std::endl;
                thread_count = std::thread::hardware_concurrency();
            }
            i++;  // Skip next argument
        }
    }
    
    UDPServer server(port, use_at_most_once, thread_count);
    server.start();
    
    return 0;
}
