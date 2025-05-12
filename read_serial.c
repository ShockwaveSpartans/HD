#include <string.h>
#include <stdio.h>
#include <math.h>
#include <stdint.h>
#include <stdlib.h>

#pragma pack(push, 1) // Ensure no padding in the struct
typedef struct {
    char riff[4];                 // "RIFF"
    int32_t flength;              // file length in bytes
    char wave[4];                 // "WAVE"
    char fmt[4];                  // "fmt "
    int32_t chunk_size;           // size of FMT chunk (16 for PCM)
    int16_t format_tag;           // 1=PCM
    int16_t num_channel;          // 1=mono, 2=stereo
    int32_t sample_rate;          // sampling rate (Hz)
    int32_t bytes_per_second;     // byte rate
    int16_t bytes_per_sample;     // bytes per sample
    int16_t bits_per_sample;      // bits per sample
    char data[4];                 // "data"
    int32_t dlength;              // data length in bytes
} wav_header;
#pragma pack(pop)

#define SAMPLE_RATE 8000
#define DURATION_SECONDS 10

int main(int argc, char *argv[]) {
    if (argc != 3) {
        fprintf(stderr, "Usage: %s <input_file> <output_file.wav>\n", argv[0]);
        return EXIT_FAILURE;
    }

    FILE *input_file = fopen(argv[1], "rb");
    if (!input_file) {
        printf("Failed to open input file");
        return 1;
    }

    const size_t buffer_size = SAMPLE_RATE * DURATION_SECONDS;
    int16_t *buffer = calloc(buffer_size, sizeof(int16_t));
    if (!buffer) {
        printf("Memory allocation failed");
        fclose(input_file);
        return 1;
    }

    // Initialize WAV header
    wav_header wavh = {
        .riff = {'R', 'I', 'F', 'F'},
        .wave = {'W', 'A', 'V', 'E'},
        .fmt = {'f', 'm', 't', ' '},
        .data = {'d', 'a', 't', 'a'},
        .chunk_size = 16,
        .format_tag = 1,          // PCM
        .num_channel = 1,         // Mono
        .sample_rate = SAMPLE_RATE,
        .bits_per_sample = 16,
        .bytes_per_sample = 2,    // 16-bit mono
        .bytes_per_second = SAMPLE_RATE * 2,
        .dlength = buffer_size * sizeof(int16_t),
        .flength = sizeof(wav_header) + buffer_size * sizeof(int16_t) - 8
    };

    // Read and convert 8-bit data to 16-bit PCM
    size_t samples_read = 0;
    uint8_t byte1;
    
    while (samples_read < buffer_size && fread(&byte1, sizeof(uint8_t), 1, input_file) == 1) {

        // Convert 8-bit unsigned [0,255] to 16-bit signed [-32768, 32767]
        int16_t sample16bit = (int16_t)(((int)byte1 - 128) * 256); // Center at 0 and scale
        buffer[samples_read++] = sample16bit;
        //printf("%d ", sample16bit);
    }

    fclose(input_file);

    // Write WAV file
    FILE *output_file = fopen(argv[2], "wb");
    if (!output_file) {
        printf("Failed to create output file");
        free(buffer);
        return EXIT_FAILURE;
    }

    // Write header and data
    fwrite(&wavh, 1, sizeof(wavh), output_file);
    fwrite(buffer, sizeof(int16_t), samples_read, output_file);

    // Clean up
    fclose(output_file);
    free(buffer);

    printf("Successfully created '%s' with %zu samples\n", argv[2], samples_read);
    return EXIT_SUCCESS;
}