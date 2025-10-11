/**
 * JSON Storage Implementation
 */

#include "../include/json_storage.h"
#include "../include/json.hpp"
#include <fstream>
#include <iostream>
#include <sys/stat.h>
#include <sys/types.h>

using json = nlohmann::json;

JsonStorage::JsonStorage(const std::string &dir)
    : data_dir(dir),
      facilities_file(dir + "/facilities.json"),
      bookings_file(dir + "/bookings.json")
{
}

bool JsonStorage::file_exists(const std::string &filepath)
{
    struct stat buffer;
    return (stat(filepath.c_str(), &buffer) == 0);
}

bool JsonStorage::create_directory(const std::string &dir)
{
#ifdef _WIN32
    return (_mkdir(dir.c_str()) == 0 || errno == EEXIST);
#else
    return (mkdir(dir.c_str(), 0755) == 0 || errno == EEXIST);
#endif
}

bool JsonStorage::initialize()
{
    // Create data directory
    if (!create_directory(data_dir))
    {
        std::cerr << "Unable to create data directory: " << data_dir << std::endl;
        return false;
    }

    // Create empty files if they don't exist
    if (!file_exists(facilities_file))
    {
        std::ofstream file(facilities_file);
        file << "{}";
        file.close();
        std::cout << "Created facilities data file: " << facilities_file << std::endl;
    }

    if (!file_exists(bookings_file))
    {
        std::ofstream file(bookings_file);
        file << "[]";
        file.close();
        std::cout << "Created bookings data file: " << bookings_file << std::endl;
    }

    std::cout << "✓ JSON storage initialization complete: " << data_dir << std::endl;
    return true;
}

bool JsonStorage::save_facilities(const std::map<std::string, Facility> &facilities)
{
    try
    {
        json j = json::object();

        for (const auto &pair : facilities)
        {
            const Facility &facility = pair.second;

            json facility_json;
            facility_json["name"] = facility.name;

            // Save bookings list
            json bookings_array = json::array();
            for (const auto &booking : facility.bookings)
            {
                json booking_json;
                booking_json["booking_id"] = booking.booking_id;
                booking_json["facility_name"] = booking.facility_name;
                booking_json["start_time"] = booking.start_time;
                booking_json["end_time"] = booking.end_time;
                bookings_array.push_back(booking_json);
            }
            facility_json["bookings"] = bookings_array;

            j[facility.name] = facility_json;
        }

        std::ofstream file(facilities_file);
        file << j.dump(2); // Formatted output with 2-space indentation
        file.close();

        return true;
    }
    catch (const std::exception &e)
    {
        std::cerr << "Failed to save facilities data: " << e.what() << std::endl;
        return false;
    }
}

bool JsonStorage::load_facilities(std::map<std::string, Facility> &facilities)
{
    try
    {
        if (!file_exists(facilities_file))
        {
            return true; // File doesn't exist, return empty map
        }

        std::ifstream file(facilities_file);
        json j;
        file >> j;
        file.close();

        facilities.clear();

        for (auto &[name, facility_json] : j.items())
        {
            Facility facility;
            facility.name = facility_json["name"];

            // Load bookings
            if (facility_json.contains("bookings"))
            {
                for (const auto &booking_json : facility_json["bookings"])
                {
                    Booking booking;
                    booking.booking_id = booking_json["booking_id"];
                    booking.facility_name = booking_json["facility_name"];
                    booking.start_time = booking_json["start_time"];
                    booking.end_time = booking_json["end_time"];
                    facility.bookings.push_back(booking);
                }
            }

            facilities[facility.name] = facility;
        }

        std::cout << "✓ Loaded " << facilities.size() << " facilities from file" << std::endl;
        return true;
    }
    catch (const std::exception &e)
    {
        std::cerr << "Failed to load facilities data: " << e.what() << std::endl;
        return false;
    }
}

bool JsonStorage::save_bookings(const std::map<uint32_t, Booking> &bookings)
{
    try
    {
        json j = json::array();

        for (const auto &pair : bookings)
        {
            const Booking &booking = pair.second;

            json booking_json;
            booking_json["booking_id"] = booking.booking_id;
            booking_json["facility_name"] = booking.facility_name;
            booking_json["start_time"] = booking.start_time;
            booking_json["end_time"] = booking.end_time;

            j.push_back(booking_json);
        }

        std::ofstream file(bookings_file);
        file << j.dump(2);
        file.close();

        return true;
    }
    catch (const std::exception &e)
    {
        std::cerr << "Failed to save bookings data: " << e.what() << std::endl;
        return false;
    }
}

bool JsonStorage::load_bookings(std::map<uint32_t, Booking> &bookings)
{
    try
    {
        if (!file_exists(bookings_file))
        {
            return true;
        }

        std::ifstream file(bookings_file);
        json j;
        file >> j;
        file.close();

        bookings.clear();

        for (const auto &booking_json : j)
        {
            Booking booking;
            booking.booking_id = booking_json["booking_id"];
            booking.facility_name = booking_json["facility_name"];
            booking.start_time = booking_json["start_time"];
            booking.end_time = booking_json["end_time"];

            bookings[booking.booking_id] = booking;
        }

        std::cout << "✓ Loaded " << bookings.size() << " bookings from file" << std::endl;
        return true;
    }
    catch (const std::exception &e)
    {
        std::cerr << "Failed to load bookings data: " << e.what() << std::endl;
        return false;
    }
}

uint32_t JsonStorage::get_next_booking_id()
{
    try
    {
        if (!file_exists(bookings_file))
        {
            return 1;
        }

        std::ifstream file(bookings_file);
        json j;
        file >> j;
        file.close();

        uint32_t max_id = 0;
        for (const auto &booking_json : j)
        {
            uint32_t id = booking_json["booking_id"];
            if (id > max_id)
            {
                max_id = id;
            }
        }

        return max_id + 1;
    }
    catch (const std::exception &e)
    {
        std::cerr << "Failed to get next booking ID: " << e.what() << std::endl;
        return 1;
    }
}
