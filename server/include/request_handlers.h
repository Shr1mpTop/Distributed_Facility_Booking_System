/**
 * Request Handlers
 * Handles all types of client requests
 */

#ifndef REQUEST_HANDLERS_H
#define REQUEST_HANDLERS_H

#include "byte_buffer.h"
#include "facility_manager.h"
#include "monitor_manager.h"
#include <netinet/in.h>

class RequestHandlers
{
private:
    FacilityManager &facility_manager;
    MonitorManager &monitor_manager;

public:
    RequestHandlers(FacilityManager &fm, MonitorManager &mm);

    // Service handlers
    ByteBuffer handle_query_availability(ByteBuffer &request);
    ByteBuffer handle_book_facility(ByteBuffer &request);
    ByteBuffer handle_change_booking(ByteBuffer &request);
    ByteBuffer handle_monitor_facility(ByteBuffer &request, const sockaddr_in &client_addr);
    ByteBuffer handle_get_last_booking_time(ByteBuffer &request);
    ByteBuffer handle_extend_booking(ByteBuffer &request);
};

#endif // REQUEST_HANDLERS_H
