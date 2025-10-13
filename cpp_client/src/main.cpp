/**
 * Main Entry Point for C++ Client
 *
 * Usage: ./cpp_client <server_ip> <server_port>
 */

#include "facility_client.h"
#include <iostream>
#include <cstdlib>

int main(int argc, char *argv[])
{
    if (argc != 3)
    {
        std::cerr << "Usage: " << argv[0] << " <server_ip> <server_port>" << std::endl;
        return 1;
    }

    std::string server_ip = argv[1];
    int server_port = std::atoi(argv[2]);

    try
    {
        FacilityBookingClient client(server_ip, server_port);
        client.run_cli();
    }
    catch (const std::exception &e)
    {
        std::cerr << "Fatal error: " << e.what() << std::endl;
        return 1;
    }

    return 0;
}
