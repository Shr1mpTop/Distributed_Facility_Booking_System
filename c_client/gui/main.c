#include <stdio.h>
#include <stdlib.h>
#include "gui_client.h"

int main(int argc, char* argv[]) {
    if (argc != 3) {
        fprintf(stderr, "Usage: %s <server_ip> <server_port>\n", argv[0]);
        return 1;
    }

    // Initialize GTK
    gtk_init(&argc, &argv);

    // Create GUI
    const char* server_ip = argv[1];
    uint16_t server_port = (uint16_t)atoi(argv[2]);
    
    FacilityBookingGUI* gui = facility_booking_gui_create(server_ip, server_port);
    if (!gui) {
        fprintf(stderr, "Failed to create GUI\n");
        return 1;
    }

    // Run main loop
    facility_booking_gui_run(gui);

    // Cleanup
    facility_booking_gui_destroy(gui);

    return 0;
}