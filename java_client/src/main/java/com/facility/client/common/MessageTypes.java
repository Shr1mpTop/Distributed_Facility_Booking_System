package com.facility.client.common;

public class MessageTypes {
    // Message type constants
    public static final int MSG_QUERY_AVAILABILITY = 1;
    public static final int MSG_BOOK_FACILITY = 2;
    public static final int MSG_CHANGE_BOOKING = 3;
    public static final int MSG_MONITOR_FACILITY = 4;
    public static final int MSG_GET_LAST_BOOKING_TIME = 5;
    public static final int MSG_EXTEND_BOOKING = 6;
    public static final int MSG_RESPONSE_SUCCESS = 100;
    public static final int MSG_RESPONSE_ERROR = 101;

    // Network constants
    public static final int TIMEOUT_SECONDS = 3;
    public static final int MAX_RETRIES = 3;
    public static final int MAX_BUFFER_SIZE = 65507;
}