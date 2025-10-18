/**
 * UDP Server Implementation with Multi-threading Support
 */

#include "../include/udp_server.h"
#include "../include/message_types.h"
#include <sys/socket.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <iostream>
#include <cstring>
#include <chrono>

UDPServer::UDPServer(int port, bool at_most_once, size_t thread_count)
    : port(port), sockfd(-1), use_at_most_once(at_most_once),
      num_threads(thread_count), shutdown_flag(false),
      total_requests(0), processed_requests(0), cached_responses(0)
{

    facility_manager.initialize();

    std::cout << "Initializing server with " << num_threads << " worker threads" << std::endl;

    // Create worker threads
    for (size_t i = 0; i < num_threads; ++i)
    {
        worker_threads.emplace_back(&UDPServer::worker_thread_func, this);
    }
}

UDPServer::~UDPServer()
{
    // Signal all threads to stop
    shutdown_flag = true;
    queue_cv.notify_all();

    // Wait for all threads to finish
    for (auto &thread : worker_threads)
    {
        if (thread.joinable())
        {
            thread.join();
        }
    }

    if (sockfd >= 0)
    {
        close(sockfd);
    }

    std::cout << "\nServer shutdown complete." << std::endl;
    print_statistics();
}

bool UDPServer::initialize_socket()
{
    sockfd = socket(AF_INET, SOCK_DGRAM, 0);
    if (sockfd < 0)
    {
        std::cerr << "Error creating socket" << std::endl;
        return false;
    }

    sockaddr_in server_addr{};
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = INADDR_ANY;
    server_addr.sin_port = htons(port);

    if (bind(sockfd, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0)
    {
        std::cerr << "Error binding socket" << std::endl;
        close(sockfd);
        return false;
    }

    return true;
}

bool UDPServer::check_cache(const ClientAddr &client_key, uint32_t request_id,
                            std::vector<uint8_t> &cached_response)
{
    std::lock_guard<std::mutex> lock(cache_mutex);

    auto client_it = response_cache.find(client_key);
    if (client_it != response_cache.end())
    {
        auto request_it = client_it->second.find(request_id);
        if (request_it != client_it->second.end())
        {
            cached_response = request_it->second.response_data;
            cached_responses++;
            return true;
        }
    }
    return false;
}

void UDPServer::cache_response(const ClientAddr &client_key, uint32_t request_id,
                               const ByteBuffer &response)
{
    std::lock_guard<std::mutex> lock(cache_mutex);

    CachedResponse cached;
    cached.response_data.assign(response.data(), response.data() + response.size());
    cached.timestamp = time(nullptr);

    response_cache[client_key][request_id] = cached;

    // Cleanup old entries if cache grows too large
    if (response_cache.size() > 1000)
    {
        cleanup_old_cache_entries();
    }
}

void UDPServer::cleanup_old_cache_entries()
{
    // Called with cache_mutex already locked
    time_t now = time(nullptr);
    const time_t MAX_CACHE_AGE = 300; // 5 minutes

    for (auto client_it = response_cache.begin(); client_it != response_cache.end();)
    {
        auto &requests = client_it->second;
        for (auto req_it = requests.begin(); req_it != requests.end();)
        {
            if (now - req_it->second.timestamp > MAX_CACHE_AGE)
            {
                req_it = requests.erase(req_it);
            }
            else
            {
                ++req_it;
            }
        }

        if (requests.empty())
        {
            client_it = response_cache.erase(client_it);
        }
        else
        {
            ++client_it;
        }
    }
}

ByteBuffer UDPServer::process_request(ByteBuffer &request, const sockaddr_in &client_addr)
{
    uint32_t request_id = request.read_uint32();
    uint8_t message_type = request.read_uint8();
    request.read_uint16(); // payload_length (for protocol consistency)

    std::cout << "[Thread " << std::this_thread::get_id() << "] Processing request ID: "
              << request_id << ", Type: " << (int)message_type << std::endl;

    ByteBuffer response;
    std::string affected_facility; // Track which facility was affected

    // Create thread-local request handler
    RequestHandlers handlers(facility_manager, monitor_manager);

    try
    {
        switch (message_type)
        {
        case QUERY_AVAILABILITY:
            response = handlers.handle_query_availability(request);
            break;

        case BOOK_FACILITY:
        {
            // Save facility name and time info before processing
            size_t saved_pos = request.position();
            affected_facility = request.read_string();
            time_t start_time = request.read_time();
            time_t end_time = request.read_time();
            request.set_position(saved_pos);

            response = handlers.handle_book_facility(request);

            // If booking successful, notify monitors
            if (response.data()[0] == RESPONSE_SUCCESS && !affected_facility.empty())
            {
                // Extract booking ID from response
                ByteBuffer resp_copy(response.data(), response.size());
                resp_copy.read_uint8(); // Skip status
                uint32_t booking_id = resp_copy.read_uint32();

                // Create booking change notification
                BookingChange change;
                change.operation = OP_BOOK;
                change.booking_id = booking_id;
                change.start_time = start_time;
                change.end_time = end_time;
                change.old_start_time = 0;
                change.old_end_time = 0;

                monitor_manager.notify_monitors(affected_facility, change, sockfd, facility_manager);
            }
            break;
        }

        case CHANGE_BOOKING:
        {
            // Get booking info before processing
            size_t saved_pos = request.position();
            uint32_t booking_id = request.read_uint32();
            request.set_position(saved_pos);

            Booking old_booking;
            if (facility_manager.booking_exists(booking_id))
            {
                old_booking = facility_manager.get_booking(booking_id);
                affected_facility = old_booking.facility_name;
            }

            response = handlers.handle_change_booking(request);

            // If change successful, notify monitors
            if (response.data()[0] == RESPONSE_SUCCESS && !affected_facility.empty())
            {
                const Booking &new_booking = facility_manager.get_booking(booking_id);

                BookingChange change;
                change.operation = OP_CHANGE;
                change.booking_id = booking_id;
                change.start_time = new_booking.start_time;
                change.end_time = new_booking.end_time;
                change.old_start_time = old_booking.start_time;
                change.old_end_time = old_booking.end_time;

                monitor_manager.notify_monitors(affected_facility, change, sockfd, facility_manager);
            }
            break;
        }

        case MONITOR_FACILITY:
            response = handlers.handle_monitor_facility(request, client_addr);
            break;

        case GET_LAST_BOOKING_TIME:
            response = handlers.handle_get_last_booking_time(request);
            break;

        case EXTEND_BOOKING:
        {
            // Get booking info before processing
            size_t saved_pos = request.position();
            uint32_t booking_id = request.read_uint32();
            request.set_position(saved_pos);

            Booking old_booking;
            if (facility_manager.booking_exists(booking_id))
            {
                old_booking = facility_manager.get_booking(booking_id);
                affected_facility = old_booking.facility_name;
            }

            response = handlers.handle_extend_booking(request);

            // If extension successful, notify monitors
            if (response.data()[0] == RESPONSE_SUCCESS && !affected_facility.empty())
            {
                const Booking &new_booking = facility_manager.get_booking(booking_id);

                BookingChange change;
                change.operation = OP_EXTEND;
                change.booking_id = booking_id;
                change.start_time = new_booking.start_time;
                change.end_time = new_booking.end_time;
                change.old_start_time = old_booking.start_time;
                change.old_end_time = old_booking.end_time;

                monitor_manager.notify_monitors(affected_facility, change, sockfd, facility_manager);
            }
            break;
        }

        default:
            response.write_uint8(RESPONSE_ERROR);
            response.write_string("Unknown message type");
            break;
        }
    }
    catch (const std::exception &e)
    {
        std::cerr << "Error processing request: " << e.what() << std::endl;
        response = ByteBuffer();
        response.write_uint8(RESPONSE_ERROR);
        response.write_string(std::string("Server error: ") + e.what());
    }

    // Prepend response with request_id
    ByteBuffer final_response;
    final_response.write_uint32(request_id);
    final_response.write_bytes(response.data(), response.size());

    processed_requests++;

    return final_response;
}

void UDPServer::worker_thread_func()
{
    std::cout << "Worker thread " << std::this_thread::get_id() << " started" << std::endl;

    while (!shutdown_flag)
    {
        RequestTask task;

        {
            std::unique_lock<std::mutex> lock(queue_mutex);

            // Wait for task or shutdown signal
            queue_cv.wait(lock, [this]
                          { return !task_queue.empty() || shutdown_flag; });

            if (shutdown_flag && task_queue.empty())
            {
                break;
            }

            if (!task_queue.empty())
            {
                task = std::move(task_queue.front());
                task_queue.pop();
            }
            else
            {
                continue;
            }
        }

        // Process the task outside the lock
        process_task(task);
    }

    std::cout << "Worker thread " << std::this_thread::get_id() << " stopped" << std::endl;
}

void UDPServer::process_task(const RequestTask &task)
{
    try
    {
        const uint8_t *buffer = task.data.data();
        size_t buffer_len = task.data.size();

        // For at-most-once, check cache first
        if (use_at_most_once)
        {
            uint32_t request_id;
            std::memcpy(&request_id, buffer, sizeof(request_id));
            request_id = ntohl(request_id);

            ClientAddr client_key;
            client_key.ip = task.client_addr.sin_addr.s_addr;
            client_key.port = task.client_addr.sin_port;

            std::vector<uint8_t> cached_response;
            if (check_cache(client_key, request_id, cached_response))
            {
                std::cout << "[Thread " << std::this_thread::get_id()
                          << "] Found cached response for request " << request_id << std::endl;

                sendto(sockfd, cached_response.data(), cached_response.size(), 0,
                       (struct sockaddr *)&task.client_addr, sizeof(task.client_addr));
                return;
            }
        }

        ByteBuffer request(buffer, buffer_len);
        ByteBuffer response = process_request(request, task.client_addr);

        // Cache response if using at-most-once
        if (use_at_most_once)
        {
            uint32_t request_id;
            std::memcpy(&request_id, buffer, sizeof(request_id));
            request_id = ntohl(request_id);

            ClientAddr client_key;
            client_key.ip = task.client_addr.sin_addr.s_addr;
            client_key.port = task.client_addr.sin_port;

            cache_response(client_key, request_id, response);
        }

        // Send response
        ssize_t sent = sendto(sockfd, response.data(), response.size(), 0,
                              (struct sockaddr *)&task.client_addr, sizeof(task.client_addr));

        if (sent < 0)
        {
            std::cerr << "Error sending response" << std::endl;
        }
        else
        {
            std::cout << "[Thread " << std::this_thread::get_id()
                      << "] Sent " << sent << " bytes response" << std::endl;
        }
    }
    catch (const std::exception &e)
    {
        std::cerr << "[Thread " << std::this_thread::get_id()
                  << "] Error: " << e.what() << std::endl;
    }
}

void UDPServer::start()
{
    if (!initialize_socket())
    {
        return;
    }

    std::cout << "\n=== Multi-threaded UDP Server ===" << std::endl;
    std::cout << "Server listening on port " << port << std::endl;
    std::cout << "Invocation semantic: " << (use_at_most_once ? "at-most-once" : "at-least-once") << std::endl;
    std::cout << "Worker threads: " << num_threads << std::endl;
    std::cout << "====================================\n"
              << std::endl;

    uint8_t buffer[MAX_BUFFER_SIZE];

    while (!shutdown_flag)
    {
        sockaddr_in client_addr{};
        socklen_t client_len = sizeof(client_addr);

        ssize_t recv_len = recvfrom(sockfd, buffer, MAX_BUFFER_SIZE, 0,
                                    (struct sockaddr *)&client_addr, &client_len);

        if (recv_len < 0)
        {
            if (!shutdown_flag)
            {
                std::cerr << "Error receiving data" << std::endl;
            }
            continue;
        }

        total_requests++;

        std::cout << "\n--- Received " << recv_len << " bytes from "
                  << inet_ntoa(client_addr.sin_addr) << ":" << ntohs(client_addr.sin_port)
                  << " (Total: " << total_requests << ")" << std::endl;

        // Create task and add to queue
        RequestTask task;
        task.data.assign(buffer, buffer + recv_len);
        task.client_addr = client_addr;
        task.receive_time = time(nullptr);

        {
            std::lock_guard<std::mutex> lock(queue_mutex);
            task_queue.push(std::move(task));
        }

        // Notify one worker thread
        queue_cv.notify_one();
    }
}

void UDPServer::print_statistics() const
{
    std::cout << "\n=== Server Statistics ===" << std::endl;
    std::cout << "Total requests received: " << total_requests << std::endl;
    std::cout << "Requests processed: " << processed_requests << std::endl;
    std::cout << "Cached responses served: " << cached_responses << std::endl;
    std::cout << "Worker threads: " << num_threads << std::endl;
    std::cout << "========================\n"
              << std::endl;
}
