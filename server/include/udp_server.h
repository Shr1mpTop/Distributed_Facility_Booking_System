/**
 * UDP Server with Multi-threading Support
 * Manages network communication and request processing using thread pool
 */

#ifndef UDP_SERVER_H
#define UDP_SERVER_H

#include "facility_manager.h"
#include "monitor_manager.h"
#include "request_handlers.h"
#include "data_structures.h"
#include <map>
#include <thread>
#include <mutex>
#include <queue>
#include <condition_variable>
#include <atomic>
#include <vector>
#include <functional>

// Request task structure
struct RequestTask
{
    std::vector<uint8_t> data;
    sockaddr_in client_addr;
    time_t receive_time;
};

class UDPServer
{
private:
    int port;
    int sockfd;
    bool use_at_most_once;
    float drop_rate; // Packet drop rate (0.0-1.0)

    // Thread pool configuration
    size_t num_threads;
    std::vector<std::thread> worker_threads;
    std::queue<RequestTask> task_queue;
    std::mutex queue_mutex;
    std::condition_variable queue_cv;
    std::atomic<bool> shutdown_flag;

    // Shared resources with thread-safe access
    FacilityManager facility_manager;
    MonitorManager monitor_manager;

    // Response cache for at-most-once semantics (thread-safe)
    std::map<ClientAddr, std::map<uint32_t, CachedResponse>> response_cache;
    std::mutex cache_mutex;

    // Statistics
    std::atomic<uint64_t> total_requests;
    std::atomic<uint64_t> processed_requests;
    std::atomic<uint64_t> cached_responses;

public:
    UDPServer(int port, bool at_most_once, size_t thread_count = 4, float drop_rate = 0.0f);
    ~UDPServer();

    // Start the server
    void start();

    // Get server statistics
    void print_statistics() const;

private:
    bool initialize_socket();
    void worker_thread_func();
    void process_task(const RequestTask &task);
    ByteBuffer process_request(ByteBuffer &request, const sockaddr_in &client_addr);
    bool check_cache(const ClientAddr &client_key, uint32_t request_id,
                     std::vector<uint8_t> &cached_response);
    void cache_response(const ClientAddr &client_key, uint32_t request_id,
                        const ByteBuffer &response);
    void cleanup_old_cache_entries();
    bool should_drop_packet() const; // Check if packet should be dropped
    void send_response_with_drop_simulation(const std::vector<uint8_t> &response_data,
                                            const sockaddr_in &client_addr);
};

#endif // UDP_SERVER_H
