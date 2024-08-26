#include <filesystem>
#include <algorithm>
#include <windows.h>// TO REMOVE LATER
#include <iostream>
#include <fstream>
#include <cstring>
#include <chrono>
#include <string>
#include <cctype>
#include <vector>
// g++ -shared -o libFileUtils.so -fPIC libFileUtils.cpp
// g++ -shared -o libFileUtils.dll -fPIC libFileUtils.cpp

namespace fs = std::filesystem;

extern "C" {
    struct Image {
        char* path;
        char* date;
    };

    struct Other {
        char* path;
        char* date;
    };

    struct Folder {
        Image* images;
        int image_count;
        Other* others;
        int other_count;
    };

    bool directoryExists(const char* path) {
        return fs::exists(path);
    }

    std::string getExtension(fs::directory_entry dir_entry) {
        std::string extension = dir_entry.path().extension().string();
        std::transform(extension.begin(), extension.end(), extension.begin(), ::toupper);
        return extension.erase(0, 1);
    }

    int moveFile(const char* path, const char* destination) {
        // ensure that the parent destination folder exists
        fs::path CONVERTdestination = destination;
        fs::path CONVERTpath = path;
        fs::path destinationFolder = CONVERTdestination.parent_path();
        if (!fs::exists(destinationFolder)) {
            try {
                fs::create_directories(destinationFolder);
            }
            catch (std::error_code ec) {
                std::cerr << "Error creating destination path " << destination << " -> " << ec << std::endl;
                return -1;
            }
        }

        // move the file
        try {
            // if (!fs::exists(CONVERTdestination)) {
            //     fs::rename(CONVERTpath, CONVERTdestination);
            // } else {
            //     // handle copy principle
            // }
            fs::rename(CONVERTpath, CONVERTdestination);
            return 0;
        }
        catch (std::error_code& ec) {
            std::cerr << "Error renaming " << path << " -> " << ec << std::endl;
            return -1;
        }
    }


    std::string getLastModified(const fs::path& imagePath) {
        try {
            auto ftime = fs::last_write_time(imagePath);
            auto sctp = std::chrono::time_point_cast<std::chrono::system_clock::duration>(ftime - fs::file_time_type::clock::now() + std::chrono::system_clock::now());
            std::time_t tt = std::chrono::system_clock::to_time_t(sctp);
            std::tm* gmt = std::gmtime(&tt);
            std::stringstream ss;
            ss << std::setfill('0')
            << std::setw(4) << (gmt->tm_year + 1900) << "-"
            << std::setw(2) << (gmt->tm_mon + 1) << "-"
            << std::setw(2) << gmt->tm_mday << "-"
            << std::setw(2) << gmt->tm_hour << "-"
            << std::setw(2) << gmt->tm_min << "-"
            << std::setw(2) << gmt->tm_sec;
            
            return ss.str();
        } catch (const fs::filesystem_error& e) {
            std::cerr << "Error: " << e.what() << '\n';
            return "";
        }
    }

    Folder* getImages(const char* imagePath) {
        try {
            std::vector<std::string> imageExtensions = {
                "JPEG", "PNG", "GIF", "WEBP", "TIFF", "HEIC", "INDD", "PSD",
                "RAW", "SVG", "EPS", "AI", "ICO", "JPG", "BMP", "MP4",
                "MOV", "WMV", "AVCHD", "FLV", "MKV", "WEBM", "OGG", "M4V", "3GP"
            };
            std::vector<Image> images;
            std::vector<Other> others;

            for (const fs::directory_entry& dir_entry: fs::recursive_directory_iterator(imagePath)) {
                if (!fs::is_directory(dir_entry.path())) {
                    std::string extension = getExtension(dir_entry);
                    auto it = std::find(imageExtensions.begin(), imageExtensions.end(), extension);
                    std::string path = dir_entry.path().string();
                    std::string date = getLastModified(dir_entry.path());

                    if (path[0] == '.') {
                        others.push_back({strdup(path.c_str()), strdup(date.c_str())});
                        continue;;
                    }
                    if (it != imageExtensions.end()) {
                        // is an image/video
                        images.push_back({strdup(path.c_str()), strdup(date.c_str())});
                    } else {
                        // is an unknown file
                        others.push_back({strdup(path.c_str()), strdup(date.c_str())});
                    }
                }
            }

            Folder* folder = new Folder();
            folder->image_count = images.size();
            folder->other_count = others.size();
            folder->images = new Image[folder->image_count];
            folder->others = new Other[folder->other_count];
            std::copy(images.begin(), images.end(), folder->images);
            std::copy(others.begin(), others.end(), folder->others);

            return folder;
        } catch (const std::exception& e) {
            std::cerr << "Error in getImages(): " << e.what() << '\n';
            return nullptr;
        }
    }

    void freeFolder(Folder* folder) {
        for (int i = 0; i < folder->image_count; ++i) {
            free(folder->images[i].path);
            free(folder->images[i].date);
        }
        for (int i = 0; i < folder->other_count; ++i) {
            free(folder->others[i].path);
            free(folder->others[i].date);
        }
        delete[] folder->images;
        delete[] folder->others;
        delete folder;
    }
}
