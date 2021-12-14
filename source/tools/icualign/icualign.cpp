#include <cstdint>
#include <cstdio>
#include <fcntl.h>
#include <sys/mman.h>
#include <sys/stat.h>

#define PAGE_SIZE 4096
#define THRESHOLD 4096

#define ERR_FILE_OPEN -1
#define ERR_FILE_STAT -2
#define ERR_MAP_FAILED -3

int MapFile(const char *filename, uint8_t **ptr) {
    // Open the file.
    int fd = open(filename, O_RDONLY, (mode_t)0600);
    if (fd == -1) {
        return ERR_FILE_OPEN;
    }

    // Get file info.
    struct stat info;
    int fstat_result = fstat(fd, &info);
    if (fstat_result == -1) {
        return ERR_FILE_STAT;
    }

    // Memory map the content of the file.
    *ptr = reinterpret_cast<uint8_t *>(mmap(nullptr, info.st_size, PROT_READ, MAP_SHARED, fd, 0));
    if (ptr == MAP_FAILED) {
        return ERR_MAP_FAILED;
    }

    // Return the file size.
    return info.st_size;
}

bool WriteFile(const char *filename, uint8_t *data, int data_size) {
    FILE *file = fopen(filename, "wb");
    if (file == nullptr) {
        return false;
    }

    for (int i = 0; i < data_size; i++) {
        fputc(data[i], file);
    }
    fclose(file);

    return true;
}

int PadData(uint8_t *data, int data_size, uint8_t *out) {
    // Size of the ICU header.
    uint16_t header_size = *((uint16_t *)&data[0]);
    // Number of files inside icudtl.dat.
    uint32_t item_count = *((uint32_t *)&data[header_size]);
    // Offset of the Table of Contents.
    int toc_offset = header_size + 4;

    // Copy everything until the beginning of the data.
    int out_offset = *((uint32_t *)&data[toc_offset + 4]) + header_size;
    for (int i = 0; i < out_offset; i++) {
        out[i] = data[i];
    }

    // Iterate over the files.
    for (int i = 0; i < item_count; i++) {
        // Offset inside the ToC for this file.
        int offset = toc_offset + (i * 8);

        // Offset of the name and the data.
        int name_offset = *((uint32_t *)&data[offset]);
        int data_offset = *((uint32_t *)&data[offset + 4]);

        // Offset of the name and the data relative to the beginning of the file.
        int name_file_offset = name_offset + header_size;
        int data_file_offset = data_offset + header_size;

        // Calculate the size of this file.
        int size;
        if (i + 1 < item_count) {
            int next_offset = toc_offset + ((i + 1) * 8);
            int next_data_offset = *((uint32_t *)&data[next_offset + 4]);
            size = next_data_offset - data_offset;
        } else {
            size = data_size - (data_offset + header_size);
        }

        // Insert padding to align files bigger than the threshold.
        if (size >= THRESHOLD && (out_offset & (PAGE_SIZE - 1)) != 0) {
            int padding = PAGE_SIZE - (out_offset & (PAGE_SIZE - 1));
            while (padding-- > 0) {
                out[out_offset++] = 0x00;
            }
        }

        // Put the new offset into the Table of Contents.
        uint32_t *out_data_offset = (uint32_t *)&out[offset + 4];
        *out_data_offset = out_offset - header_size;

        // Copy the content of the file.
        for (int j = 0; j < size; j++) {
            out[out_offset++] = data[data_file_offset + j];
        }
    }

    // Return the size of the output file.
    return out_offset;
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
    int data_size = MapFile(infilename, &data);
    if (data_size == -1) {
        fprintf(stderr, "icualign: error reading input file\n\n");
        return 1;
    }

    // Allocate space for the output file.
    uint8_t *out_data = new uint8_t[data_size * 2];
    // Apply padding to the file to achieve the desired alignment.
    int out_data_size = PadData(data, data_size, out_data);
    // Write the output file.
    if (!WriteFile(outfilename, out_data, out_data_size)) {
        fprintf(stderr, "icualign: error writing output file\n\n");
        return 1;
    }

    return 0;
}
