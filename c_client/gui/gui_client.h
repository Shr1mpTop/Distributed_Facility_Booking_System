#ifndef GUI_CLIENT_H
#define GUI_CLIENT_H

#include <gtk/gtk.h>
#include "../common/network_client.h"

typedef struct {
    NetworkClient* network;
    GtkWidget* window;
    GtkWidget* facility_list;
    GtkWidget* date_entry;
    GtkWidget* start_time_entry;
    GtkWidget* duration_entry;
    GtkWidget* booking_text_view;
    GtkTextBuffer* booking_buffer;
} FacilityBookingGUI;

// Initialize and cleanup
FacilityBookingGUI* facility_booking_gui_create(const char* server_ip, uint16_t server_port);
void facility_booking_gui_destroy(FacilityBookingGUI* gui);

// Main run function
void facility_booking_gui_run(FacilityBookingGUI* gui);

#endif // GUI_CLIENT_H