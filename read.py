import serial
import sys, subprocess, time, os

# Configuration
CHUNK_SIZE = 500         # Size of each read
SAMPLE_RATE = 6400
TIME = 10
#the wav file will be 5 second
TOTAL_BYTES = TIME * SAMPLE_RATE 
#TOTAL_BYTES = 100 * 1024  

# Open serial port
ser = serial.Serial(port="COM10", baudrate = 230400, bytesize=8, parity="N", stopbits=1, timeout=5)

print(f"[INFO] Serial port opened: {ser.name}")

# Open binary file for writing raw ADC data
with open("Transfer_ADC_values.data", "ab") as file:
    bytes_read = 0
    while bytes_read < TOTAL_BYTES:
        chunk = ser.read(CHUNK_SIZE)  # Read 500 bytes
        if not chunk:  # Handle potential read errors
            print("\n No data received. Check serial connection.")
            break
        file.write(chunk)             # Write to file
        bytes_read += len(chunk)
        print(f"[INFO] {bytes_read}/{TOTAL_BYTES} bytes received...", end='\r')

# Close serial port
ser.close()
print("\nData sampling complete.")



print("\n")
file.close()
#file_2.close()
ser.close()
compileResult = subprocess.getstatusoutput(f"gcc read_serial.c -o read_serial")
codeOutput = subprocess.getstatusoutput(f"read_serial Transfer_ADC_values.data transfer.wav") #runs the executable with command line arguments
print(compileResult[0]) #prints 0 if compiled with no issues
print(compileResult[1]) #prints compilation errors, if any
print(codeOutput[0]) #prints 0 if the C program could run without any errors
print(codeOutput[1]) #prints any output displayed onto the terminal by the C program