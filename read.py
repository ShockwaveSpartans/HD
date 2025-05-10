import serial
import wave
import numpy as np
import time

# Constants
SAMPLE_RATE = 6500
RECORD_TIME = 5  # Time in seconds to record

# Set serial UART parameters
ser = serial.Serial(port="COM13", baudrate=230400, bytesize=8, parity="N", stopbits=1, timeout=5)

# Check if serial communication is active
print(ser.name)

# Calculate the number of bytes to read for 5 seconds
num_bytes_to_read = SAMPLE_RATE * RECORD_TIME

# Start time tracking
start_time = time.time()

# Read the data for the specified duration
data = bytearray()
while len(data) < num_bytes_to_read:
    if ser.in_waiting:
        data += ser.read(ser.in_waiting)  # Read all available data
    # Ensure we capture for 5 seconds, even if there is a slight delay in UART
    elapsed_time = time.time() - start_time
    if elapsed_time >= RECORD_TIME:
        break

# Ensure we only have the exact number of bytes needed
data = data[:num_bytes_to_read]

# Save the data as a WAV file
with wave.open("raw_ADC_values.wav", "wb") as wav_file:
    wav_file.setnchannels(1)    # Mono
    wav_file.setsampwidth(1)    # 8-bit samples
    wav_file.setframerate(SAMPLE_RATE)
    wav_file.writeframes(data)

# Close serial port
ser.close()

print(f"Recorded {len(data)} bytes in {RECORD_TIME} seconds.")
