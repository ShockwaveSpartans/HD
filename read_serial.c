#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

void write_little_endian_uint16(uint16_t value, FILE *file) {
    fputc(value & 0xFF, file);
    fputc((value >> 8) & 0xFF, file);
}

void write_little_endian_uint32(uint32_t value, FILE *file) {
    fputc(value & 0xFF, file);
    fputc((value >> 8) & 0xFF, file);
    fputc((value >> 16) & 0xFF, file);
    fputc((value >> 24) & 0xFF, file);
}

int main(int argc, char *argv[]) {
    if (argc != 3) {
        printf("Usage: %s input.txt output.wav\n", argv[0]);
        return 1;
    }

    FILE *input = fopen(argv[1], "r");
    if (!input) {
        perror("Failed to open input");
        return 1;
    }

    int16_t *samples = NULL;
    int count = 0, temp;

    while (fscanf(input, "%d", &temp) == 1) {
        count++;
    }
    rewind(input);

    samples = malloc(count * sizeof(int16_t));
    if (!samples) {
        perror("Memory allocation failed");
        fclose(input);
        return 1;
    }

    int index = 0;
    while (fscanf(input, "%d", &temp) == 1 && index < count) {
        samples[index++] = (int16_t)((temp - 2048) * 16);
    }
    fclose(input);

    if (count == 0) {
        fprintf(stderr, "No valid samples.\n");
        free(samples);
        return 1;
    }

    FILE *output = fopen(argv[2], "wb");
    if (!output) {
        perror("Failed to create output");
        free(samples);
        return 1;
    }

    const uint32_t sample_rate = 6400;
    const uint16_t num_channels = 1;
    const uint32_t byte_rate = sample_rate * num_channels * 2; // 16 bits per sample
    const uint32_t data_size = count * 2; // 2 bytes per sample
    const uint32_t chunk_size = 36 + data_size;

    // RIFF header
    fwrite("RIFF", 4, 1, output);
    write_little_endian_uint32(chunk_size, output);
    fwrite("WAVE", 4, 1, output);

    // fmt subchunk
    fwrite("fmt ", 4, 1, output);
    write_little_endian_uint32(16, output); // Subchunk1Size (16 for PCM)
    write_little_endian_uint16(1, output);  // AudioFormat (PCM)
    write_little_endian_uint16(num_channels, output);
    write_little_endian_uint32(sample_rate, output);
    write_little_endian_uint32(byte_rate, output);
    write_little_endian_uint16(2, output);  // BlockAlign (2 bytes per sample for 16-bit mono)
    write_little_endian_uint16(16, output); // Bits per sample

    // data subchunk
    fwrite("data", 4, 1, output);
    write_little_endian_uint32(data_size, output);
    for (int i = 0; i < count; i++) {
        write_little_endian_uint16((uint16_t)samples[i], output);
    }

    fclose(output);
    free(samples);
    printf("Created %d-sample WAV file (%.1f seconds)\n", 
           count, (float)count / sample_rate);
    return 0;
}