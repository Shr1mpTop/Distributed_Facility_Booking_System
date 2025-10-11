#include "gui_client.h"
#include "../common/message_types.h"
#include <stdio.h>
#include <string.h>
#include <time.h>

static void on_query_clicked(GtkButton* button, gpointer user_data) {
    FacilityBookingGUI* gui = (FacilityBookingGUI*)user_data;
    
    // Get date and time from entries
    const char* date_str = gtk_entry_get_text(GTK_ENTRY(gui->date_entry));
    const char* time_str = gtk_entry_get_text(GTK_ENTRY(gui->start_time_entry));
    const char* duration_str = gtk_entry_get_text(GTK_ENTRY(gui->duration_entry));
    
    // Create request buffer
    ByteBuffer* request = byte_buffer_create();
    byte_buffer_write_uint8(request, MSG_QUERY_AVAILABILITY);
    byte_buffer_write_string(request, date_str);
    byte_buffer_write_string(request, time_str);
    byte_buffer_write_string(request, duration_str);
    
    // Send request
    ByteBuffer* response = byte_buffer_create();
    if (network_client_send_request(gui->network, request, response) == 0) {
        uint8_t msg_type = byte_buffer_read_uint8(response);
        if (msg_type == MSG_RESPONSE_SUCCESS) {
            char* result = byte_buffer_read_string(response);
            GtkTextIter end;
            gtk_text_buffer_get_end_iter(gui->booking_buffer, &end);
            gtk_text_buffer_insert(gui->booking_buffer, &end, result, -1);
            free(result);
        } else {
            char* error = byte_buffer_read_string(response);
            GtkWidget* dialog = gtk_message_dialog_new(GTK_WINDOW(gui->window),
                GTK_DIALOG_MODAL,
                GTK_MESSAGE_ERROR,
                GTK_BUTTONS_OK,
                "Error: %s", error);
            gtk_dialog_run(GTK_DIALOG(dialog));
            gtk_widget_destroy(dialog);
            free(error);
        }
    }
    
    byte_buffer_destroy(request);
    byte_buffer_destroy(response);
}

static void on_book_clicked(GtkButton* button, gpointer user_data) {
    FacilityBookingGUI* gui = (FacilityBookingGUI*)user_data;
    
    // Similar implementation to query but with MSG_BOOK_FACILITY
    // ...
}

static void setup_gui(FacilityBookingGUI* gui) {
    // Create main window
    gui->window = gtk_window_new(GTK_WINDOW_TOPLEVEL);
    gtk_window_set_title(GTK_WINDOW(gui->window), "Facility Booking System - Client");
    gtk_window_set_default_size(GTK_WINDOW(gui->window), 900, 700);
    g_signal_connect(gui->window, "destroy", G_CALLBACK(gtk_main_quit), NULL);
    
    // Create main vertical box
    GtkWidget* vbox = gtk_box_new(GTK_ORIENTATION_VERTICAL, 10);
    gtk_container_add(GTK_CONTAINER(gui->window), vbox);
    
    // Top info bar
    char server_info[100];
    snprintf(server_info, sizeof(server_info), "Server: %s:%d", 
             gui->network->server_ip, gui->network->server_port);
    GtkWidget* info_label = gtk_label_new(server_info);
    gtk_box_pack_start(GTK_BOX(vbox), info_label, FALSE, FALSE, 5);
    
    // Input area
    GtkWidget* input_grid = gtk_grid_new();
    gtk_grid_set_column_spacing(GTK_GRID(input_grid), 5);
    gtk_grid_set_row_spacing(GTK_GRID(input_grid), 5);
    gtk_box_pack_start(GTK_BOX(vbox), input_grid, FALSE, FALSE, 5);
    
    // Date input
    GtkWidget* date_label = gtk_label_new("Date (YYYY-MM-DD):");
    gtk_grid_attach(GTK_GRID(input_grid), date_label, 0, 0, 1, 1);
    gui->date_entry = gtk_entry_new();
    gtk_grid_attach(GTK_GRID(input_grid), gui->date_entry, 1, 0, 1, 1);
    
    // Time input
    GtkWidget* time_label = gtk_label_new("Start Time (HH:MM):");
    gtk_grid_attach(GTK_GRID(input_grid), time_label, 0, 1, 1, 1);
    gui->start_time_entry = gtk_entry_new();
    gtk_grid_attach(GTK_GRID(input_grid), gui->start_time_entry, 1, 1, 1, 1);
    
    // Duration input
    GtkWidget* duration_label = gtk_label_new("Duration (minutes):");
    gtk_grid_attach(GTK_GRID(input_grid), duration_label, 0, 2, 1, 1);
    gui->duration_entry = gtk_entry_new();
    gtk_grid_attach(GTK_GRID(input_grid), gui->duration_entry, 1, 2, 1, 1);
    
    // Buttons
    GtkWidget* button_box = gtk_button_box_new(GTK_ORIENTATION_HORIZONTAL);
    gtk_box_pack_start(GTK_BOX(vbox), button_box, FALSE, FALSE, 5);
    
    GtkWidget* query_button = gtk_button_new_with_label("Query Availability");
    g_signal_connect(query_button, "clicked", G_CALLBACK(on_query_clicked), gui);
    gtk_container_add(GTK_CONTAINER(button_box), query_button);
    
    GtkWidget* book_button = gtk_button_new_with_label("Book Facility");
    g_signal_connect(book_button, "clicked", G_CALLBACK(on_book_clicked), gui);
    gtk_container_add(GTK_CONTAINER(button_box), book_button);
    
    // Results area
    GtkWidget* scroll = gtk_scrolled_window_new(NULL, NULL);
    gtk_scrolled_window_set_policy(GTK_SCROLLED_WINDOW(scroll),
                                 GTK_POLICY_AUTOMATIC,
                                 GTK_POLICY_AUTOMATIC);
    gtk_box_pack_start(GTK_BOX(vbox), scroll, TRUE, TRUE, 5);
    
    GtkWidget* text_view = gtk_text_view_new();
    gui->booking_buffer = gtk_text_view_get_buffer(GTK_TEXT_VIEW(text_view));
    gtk_container_add(GTK_CONTAINER(scroll), text_view);
}

FacilityBookingGUI* facility_booking_gui_create(const char* server_ip, uint16_t server_port) {
    FacilityBookingGUI* gui = (FacilityBookingGUI*)malloc(sizeof(FacilityBookingGUI));
    if (gui) {
        gui->network = network_client_create(server_ip, server_port);
        if (!gui->network) {
            free(gui);
            return NULL;
        }
        setup_gui(gui);
    }
    return gui;
}

void facility_booking_gui_destroy(FacilityBookingGUI* gui) {
    if (gui) {
        network_client_destroy(gui->network);
        free(gui);
    }
}

void facility_booking_gui_run(FacilityBookingGUI* gui) {
    gtk_widget_show_all(gui->window);
    gtk_main();
}