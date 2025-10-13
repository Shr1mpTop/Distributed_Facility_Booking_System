# Java GUI Client for Facility Booking System

This is a Java Swing GUI client for the Facility Booking System. It provides the same functionality as the Python GUI client.

## Features

- **Query Availability**: Query available time slots for facilities
- **Book Facility**: Book a facility for a specific time period
- **Change Booking**: Modify an existing booking's time
- **Get Last Booking Time**: Query the last booking end time for a facility (idempotent operation)
- **Extend Booking**: Extend the duration of an existing booking (non-idempotent operation)

## Requirements

- Java 11 or higher
- Maven 3.6 or higher

## Building

To build the project, run:

```bash
mvn clean package
```

This will create a fat JAR file `target/facility-client-gui.jar` that includes all dependencies.

## Running

### Using the JAR file:

```bash
java -jar target/facility-client-gui.jar <server_ip> <server_port>
```

Example:
```bash
java -jar target/facility-client-gui.jar 127.0.0.1 8080
```

### Using Maven:

```bash
mvn exec:java -Dexec.mainClass="com.facility.gui.FacilityBookingGUI" -Dexec.args="127.0.0.1 8080"
```

### Using the run script:

```bash
./run.sh 127.0.0.1 8080
```

## Usage

1. **Query Availability**
   - Select a facility from the dropdown
   - Enter days to query (comma-separated, 0=today, 1=tomorrow, etc.)
   - Click "Query" to see available time slots

2. **Book Facility**
   - Select a facility
   - Enter date (YYYY-MM-DD format)
   - Enter start time (HH:MM format)
   - Enter duration in hours
   - Click "Book Facility"
   - Note the confirmation ID for future operations

3. **Change Booking**
   - Enter the confirmation ID from your booking
   - Enter time offset in minutes (positive to move later, negative for earlier)
   - Click "Change Booking"

4. **Get Last Booking Time**
   - Select a facility
   - Click "Query Last Booking Time"
   - View the last booking end time for that facility

5. **Extend Booking**
   - Enter the confirmation ID
   - Enter extension time in minutes
   - Click "Extend Booking"

## Project Structure

```
java_client/
├── pom.xml                          # Maven configuration
├── README.md                        # This file
├── run.sh                          # Run script
└── src/
    └── main/
        └── java/
            └── com/
                └── facility/
                    ├── common/
                    │   ├── ByteBuffer.java      # Data serialization
                    │   ├── MessageTypes.java    # Protocol constants
                    │   └── NetworkClient.java   # UDP communication
                    └── gui/
                        └── FacilityBookingGUI.java  # Main GUI application
```

## Network Protocol

The client communicates with the server using UDP with the following message format:

```
Request:
  [Request ID: 4 bytes]
  [Message Type: 1 byte]
  [Payload Length: 2 bytes]
  [Payload: variable]

Response:
  [Request ID: 4 bytes]
  [Status: 1 byte (100=success, 101=error)]
  [Payload: variable]
```

## Notes

- The client implements retry logic (3 attempts by default) for at-least-once semantics
- Network timeout is set to 3 seconds per attempt
- All operations run in background threads to keep the GUI responsive
- The log area at the bottom shows operation status and timestamps
