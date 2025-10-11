/**
 * JSON Storage Manager
 * Uses JSON files for data persistence
 * Simple, lightweight, zero dependencies (except json.hpp single header)
 */

#ifndef JSON_STORAGE_H
#define JSON_STORAGE_H

#include "data_structures.h"
#include <string>
#include <vector>
#include <map>

class JsonStorage
{
private:
    std::string data_dir;
    std::string facilities_file;
    std::string bookings_file;

public:
    JsonStorage(const std::string &dir = "data");

    // 初始化存储目录
    bool initialize();

    // 设施操作
    bool save_facilities(const std::map<std::string, Facility> &facilities);
    bool load_facilities(std::map<std::string, Facility> &facilities);

    // 预订操作
    bool save_bookings(const std::map<uint32_t, Booking> &bookings);
    bool load_bookings(std::map<uint32_t, Booking> &bookings);

    // 获取下一个可用的预订ID
    uint32_t get_next_booking_id();

    // 工具函数
    bool file_exists(const std::string &filepath);
    bool create_directory(const std::string &dir);
};

#endif // JSON_STORAGE_H
