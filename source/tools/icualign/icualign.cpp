// © 2016 and later: Unicode, Inc. and others.
// License & terms of use: http://www.unicode.org/copyright.html

#include <errno.h>
#include <fcntl.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>

#include <vector>

#define HANDLE_EINTR(x)                                                                                 \
    ({                                                                                                  \
        decltype(x) eintr_wrapper_result;                                                               \
        do {                                                                                            \
            eintr_wrapper_result = (x);                                                                 \
        } while (eintr_wrapper_result == -1 && errno == EINTR);                                         \
        eintr_wrapper_result;                                                                           \
    })

constexpr size_t kPageSize = 4096;
constexpr size_t kThreshold = 8192;

constexpr ssize_t kErrFileOpen = -1;
constexpr ssize_t kErrFileStat = -2;
constexpr ssize_t kErrMapFailed = -3;

// Given a filename, maps a file into memory.
// Returns the address of the data via `data`.
// Returns the size of the file as a return value.
ssize_t MapFile(const char *filename, uint8_t **data) {
    int fd = HANDLE_EINTR(open(filename, O_RDONLY, static_cast<mode_t>(0600)));
    if (fd == -1) {
        perror("open");
        return kErrFileOpen;
    }

    struct stat info;
    int fstat_result = fstat(fd, &info);
    if (fstat_result == -1) {
        close(fd);
        perror("fstat");
        return kErrFileStat;
    }

    // Memory map the content of the file.
    *data = reinterpret_cast<uint8_t *>(mmap(nullptr, info.st_size, PROT_READ, MAP_SHARED, fd, 0));
    close(fd);
    if (data == MAP_FAILED) {
        perror("mmap");
        return kErrMapFailed;
    }

    return info.st_size;
}

// Given a filename, write data into the corresponding file.
// Returns true if writing was successful, false otherwise.
bool WriteFile(const char *filename, const std::vector<uint8_t> &out_data) {
    FILE *file = fopen(filename, "wb");
    if (file == nullptr) {
        perror("fopen");
        return false;
    }

    size_t bytes_written = fwrite(out_data.data(), 1, out_data.size(), file);
    if (bytes_written < out_data.size()) {
        perror("fwrite");
        return false;
    }

    fclose(file);
    return true;
}

// Read 16 bits from an array of bytes.
uint16_t Read16(uint8_t *data, size_t offset) { return data[offset] | (data[offset + 1] << 8); }

// Read 32 bits from an array of bytes.
uint32_t Read32(uint8_t *data, size_t offset) {
    return (data[offset] | (data[offset + 1] << 8) | (data[offset + 2] << 16) |
            (data[offset + 3] << 24));
}

// Write 32 bits into a vector of bytes.
void Write32(std::vector<uint8_t> &data, size_t offset, uint32_t value) {
    data[offset + 0] = (value >> 0) & 0xFF;
    data[offset + 1] = (value >> 8) & 0xFF;
    data[offset + 2] = (value >> 16) & 0xFF;
    data[offset + 3] = (value >> 24) & 0xFF;
}

/*-------------------------------------------------------------------------------
  (Adapted from `tools/toolutil/pkg_gencmn.cpp`)

  A .dat package file contains a simple Table of Contents of item names,
  followed by the items themselves:

  1. ToC table

  uint32_t count; - number of items
  UDataOffsetTOCEntry entry[count]; - pair of uint32_t values per item:
      uint32_t nameOffset; - offset of the item name
      uint32_t dataOffset; - offset of the item data
  both are byte offsets from the beginning of the data

  2. item name strings

  All item names are stored as char * strings in one block between the ToC table
  and the data items.

  3. data items

  The data items are stored following the item names block.
  The data items are stored in the sorted order of their names.
-------------------------------------------------------------------------------*/

// Given the input data and its size, return a vector with the padded output data.
std::vector<uint8_t> PadData(uint8_t *data, int data_size) {
    std::vector<uint8_t> out;

    size_t header_size = Read16(data, 0);          // Size of the ICU header.
    size_t item_count = Read32(data, header_size); // Number of files inside icudtl.dat.
    size_t toc_offset = header_size + 4;           // Offset of the Table of Contents.

    // Copy everything until the beginning of the data.
    size_t out_offset = Read32(data, toc_offset + 4) + header_size;
    for (size_t i = 0; i < out_offset; i++) {
        out.push_back(data[i]);
    }

    // Iterate over the files.
    for (size_t i = 0; i < item_count; i++) {
        // Offset inside the ToC for this file.
        size_t offset = toc_offset + (i * 8);

        // Offset of the name and data, relative to the beginning of the data section.
        size_t name_offset = Read32(data, offset);
        size_t data_offset = Read32(data, offset + 4);

        // Offset of the name and the data, relative to the beginning of the file.
        size_t name_file_offset = name_offset + header_size;
        size_t data_file_offset = data_offset + header_size;

        // Calculate the size of this file.
        size_t size;
        if (i + 1 < item_count) {
            size_t next_offset = toc_offset + ((i + 1) * 8);
            size_t next_data_offset = Read32(data, next_offset + 4);
            size = next_data_offset - data_offset;
        } else {
            size = data_size - (data_offset + header_size);
        }

        // Insert padding to align files bigger than the threshold.
        size_t page_offset = out_offset & (kPageSize - 1);
        if (size >= kThreshold && page_offset != 0) {
            size_t padding = kPageSize - page_offset;
            out.insert(out.end(), padding, 0x00);
            out_offset += padding;
        }

        // Put the new offset into the Table of Contents.
        Write32(out, offset + 4, out_offset - header_size);

        // Copy the content of the file.
        out.insert(out.end(), &data[data_file_offset], &data[data_file_offset] + size);
        out_offset += size;
    }

    return out;
}

void PrintHelp() { fprintf(stderr, "usage: icualign <infilename> <outfilename>\n"); }

int main(int argc, const char *argv[]) {
    // Check arguments.
    if (argc != 3) {
        fprintf(stderr, "icualign: wrong number of arguments\n\n");
        PrintHelp();
        return 1;
    }

    // Extract arguments.
    const char *infilename = argv[1];
    const char *outfilename = argv[2];

    // Map the input file.
    uint8_t *data;
    ssize_t data_size = MapFile(infilename, &data);
    if (data_size < 0) {
        fprintf(stderr, "icualign: error reading input file\n\n");
        return 1;
    }

    // Apply padding to the file to achieve the desired alignment.
    std::vector<uint8_t> out_data = PadData(data, data_size);
    munmap(data, data_size);

    // Write the output file.
    if (!WriteFile(outfilename, out_data)) {
        fprintf(stderr, "icualign: error writing output file\n\n");
        return 1;
    }

    return 0;
}
