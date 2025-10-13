# Server Monitor

Real-time monitoring tools for the Distributed Facility Booking System server.

## Features

- **Real-time log monitoring** - Monitor server activity as it happens
- **Thread tracking** - See which worker thread processes each request
- **Statistics tracking** - Track requests, responses, and errors
- **Color-coded output** - Easy-to-read visualization (GUI)
- **Two interfaces** - Command-line and GUI options

## Quick Start

### Command-Line Monitor

Real-time monitoring (tail mode):
```bash
python monitor/realtime_monitor.py tail
```

Analyze existing log:
```bash
python monitor/realtime_monitor.py analyze
```

Custom log file:
```bash
python monitor/realtime_monitor.py tail server.log
```

### GUI Monitor

Launch the graphical monitor:
```bash
python monitor/monitor_gui.py
```

With custom log file:
```bash
python monitor/monitor_gui.py server.log
```

## What It Monitors

The monitor tracks:
- 📨 **Received requests** - Incoming client requests with source IP
- 🔍 **Query operations** - Facility availability queries
- 📝 **Booking operations** - New facility bookings
- ✏️ **Change operations** - Booking modifications
- �️ **Monitor operations** - Facility monitoring registrations
- 🕐 **Time queries** - Last booking time requests
- ⏱️ **Extend operations** - Booking time extensions
- 💓 **Heartbeat** - Keep-alive/monitor messages
- 📤 **Responses sent** - Server responses with byte count
- ✅ **Success events** - Booking creation confirmations
- ❌ **Errors** - Server errors and issues
- 🧵 **Thread info** - Which worker thread handled the request

## Message Types with Emojis

| Code | Type | Emoji |
|------|------|-------|
| 1 | QUERY_AVAILABILITY | 🔍 |
| 2 | BOOK_FACILITY | 📝 |
| 3 | CHANGE_BOOKING | ✏️ |
| 4 | MONITOR_FACILITY | 👁️ |
| 5 | GET_LAST_BOOKING_TIME | 🕐 |
| 6 | EXTEND_BOOKING | ⏱️ |
| 111 | HEARTBEAT/MONITOR | 💓 |

## Usage Example

1. Start the server:
```bash
./bin/server
```

2. In another terminal, start the monitor:
```bash
python monitor/monitor_gui.py
```

3. Click "Start Monitoring" in the GUI

4. Run client operations and watch them appear in real-time!

## Output Example

```
[14:23:45] 📨 Received 28 bytes from 127.0.0.1:51655
[14:23:45] [T:9bb000] 💓 Processing: HEARTBEAT (ID: 16781635)
[14:23:45] [T:9bb000] 📤 Response sent: 27 bytes
[14:23:46] 📨 Received 34 bytes from 127.0.0.1:63517
[14:23:46] [T:c77000] 📝 Processing: BOOK_FACILITY (ID: 4)
## Output Example

```
[14:23:45] RECEIVED: 28 bytes from 127.0.0.1:51655
[14:23:45] [T:9bb000] PROCESSING: HEARTBEAT (ID: 16781635)
[14:23:45] [T:9bb000] SENT: 27 bytes
[14:23:46] RECEIVED: 34 bytes from 127.0.0.1:63517
[14:23:46] [T:c77000] PROCESSING: BOOK_FACILITY (ID: 4)
[14:23:46] [T:c77000] Book facility: Conference_Room_B
[14:23:46] [T:c77000] SENT: 30 bytes
[14:23:47] RECEIVED: 24 bytes from 127.0.0.1:63517
[14:23:47] [T:d8f000] PROCESSING: BOOK_FACILITY (ID: 12)
[14:23:47] [T:d8f000] Book facility: Lab_101
[14:23:47] [T:d8f000] Booking created: ID 63
[14:23:47] [T:d8f000] SENT: 9 bytes
[14:23:48] RECEIVED: 46 bytes from 127.0.0.1:63517
[14:23:48] [T:b5f000] PROCESSING: QUERY_AVAILABILITY (ID: 13)
[14:23:48] [T:b5f000] Query availability for: Conference_Room_A
[14:23:48] [T:b5f000] SENT: 415 bytes
```

**Thread ID format**: `[T:xxxxxx]` shows the last 6 hex digits of the thread ID
[14:23:46] [T:c77000] 📤 Response sent: 30 bytes
[14:23:47] 📨 Received 24 bytes from 127.0.0.1:63517
[14:23:47] [T:d8f000] 📝 Processing: BOOK_FACILITY (ID: 12)
[14:23:47] [T:d8f000] � Book facility: Lab_101
[14:23:47] [T:d8f000] ✅ Booking created: ID 63
[14:23:47] [T:d8f000] 📤 Response sent: 9 bytes
[14:23:48] 📨 Received 46 bytes from 127.0.0.1:63517
[14:23:48] [T:b5f000] 🔍 Processing: QUERY_AVAILABILITY (ID: 13)
[14:23:48] [T:b5f000] 🔧 Query availability for: Conference_Room_A
[14:23:48] [T:b5f000] 📤 Response sent: 415 bytes
```

**Thread ID format**: `[T:xxxxxx]` shows the last 6 hex digits of the thread ID

## Requirements

- Python 3.6+
- tkinter (for GUI monitor, usually included with Python)

## Notes

- The monitor reads from `server.log` by default
- Must start the server first to generate the log file
- Press Ctrl+C to stop the command-line monitor
- GUI monitor automatically stops when window is closed
- Statistics are displayed when stopping the monitor

## Architecture

Both monitors use a log file tailing approach:
- Open the log file and seek to the end
- Read new lines as they're written
- Parse and display events in real-time
- Track statistics throughout the session
