/**
 * Main Entry Point for C++ Client
 *
 * Usage: ./cpp_client [server_ip] [server_port] [--drop-rate rate]
 */

#include "facility_client.h"
#include <iostream>
#include <cstdlib>
#include <cstring>

int main(int argc, char *argv[])
{
    std::string server_ip = "8.148.159.175";
    int server_port = 8080;
    double drop_rate = 0.0;

    // Parse command line arguments
    for (int i = 1; i < argc; ++i)
    {
        if (strcmp(argv[i], "--drop-rate") == 0)
        {
            if (i + 1 < argc)
            {
                drop_rate = std::atof(argv[++i]);
                if (drop_rate < 0.0 || drop_rate > 1.0)
                {
                    std::cerr << "Error: drop-rate must be between 0.0 and 1.0" << std::endl;
                    return 1;
                }
            }
            else
            {
                std::cerr << "Error: --drop-rate requires a value" << std::endl;
                return 1;
            }
        }
        else if (argv[i][0] == '-')
        {
            std::cerr << "Unknown option: " << argv[i] << std::endl;
            std::cerr << "Usage: " << argv[0] << " [server_ip] [server_port] [--drop-rate rate]" << std::endl;
            return 1;
        }
        else
        {
            // Positional arguments
            if (i == 1)
            {
                server_ip = argv[i];
            }
            else if (i == 2)
            {
                server_port = std::atoi(argv[i]);
            }
            else
            {
                std::cerr << "Too many positional arguments" << std::endl;
                std::cerr << "Usage: " << argv[0] << " [server_ip] [server_port] [--drop-rate rate]" << std::endl;
                return 1;
            }
        }
    }

    std::cout << "Connecting to server: " << server_ip << ":" << server_port << std::endl;
    if (drop_rate > 0.0)
    {
        std::cout << "Packet drop rate: " << drop_rate << std::endl;
    }

    try
    {
        FacilityBookingClient client(server_ip, server_port, drop_rate);
        client.run_cli();
    }
    catch (const std::exception &e)
    {
        std::cerr << "Fatal error: " << e.what() << std::endl;
        return 1;
    }

    return 0;
}
