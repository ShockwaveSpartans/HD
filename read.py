import serial
import numpy as np
import sys, subprocess, time, os
import matplotlib.pyplot as plt
import csv


# Open serial port
ser = serial.Serial(port="COM10", baudrate = 921600, bytesize=8, parity="N", stopbits=1, timeout=5)

print(f"Serial port: {ser.name}")

print("\n")
print("====================================================================")
print("Welcome to the main menu")
print("\nPlease choose a operating mode:")
print("\n1. Manual Recording Mode")
print("\n2. Distance Trigger Mode")
print("====================================================================")
print("\n")

user_input = int(input("\nEnter an option: \n"))
print("\n")

if user_input == 1:
    print("====================================================================")
    print("You have selected Manual Recording Mode ")
    print("====================================================================")

    time_input = float(input("\nEnter a time(second): \n"))


if user_input == 2:
    print("====================================================================")
    print("You have selected Distance Trigger Mode ")
    print("====================================================================")


# Configuration
CHUNK_SIZE = 1000         # Size of each read
SAMPLE_RATE = 10000
music_length = time_input * 2   #the wav file will be time input * 2 second
TOTAL_BYTES = music_length * SAMPLE_RATE 
#TOTAL_BYTES = 100 * 1024  

amplitude_list = []

print("\n\n")
print("====================================================================")
print("Data sampling starting...")
print("====================================================================")
print("\n\n")


# Open binary file for writing raw ADC data
with open("2outlier_ADC_values.data", "ab") as file:
    bytes_read = 0
    while bytes_read < TOTAL_BYTES:
        # read in chunk size
        chunk = ser.read(CHUNK_SIZE)
        #check if there is data receive
        if not chunk:  
            print("\n No data received.")
            break
        file.write(chunk)             # Write to file

        # convert the raw binary into decimal then append it
        for i in range(0, len(chunk), 2):
            decimal_chunk = int.from_bytes(chunk[i:i+2], byteorder='little')
            amplitude_list.append(decimal_chunk)

        # check the total byte size received
        bytes_read += len(chunk)
        print(f"{bytes_read}/{TOTAL_BYTES} bytes received...", end='\r')
  
# Close serial port
ser.close()
print("\n\n\n")
print("====================================================================")
print("Data sampling complete.")
print("====================================================================")




# Plot Graph
half_samples = len(amplitude_list) // 2
half_amplitude_list = amplitude_list[:half_samples]
timing = np.linspace(0, time_input, len(half_amplitude_list))                # Time from 0 to input time (second)

plt.figure(figsize=(10, 4))
plt.plot(timing, half_amplitude_list, label='ADC Value')
plt.title('ADC value vs Time Waveform')
plt.xlabel('Time (s)')
plt.ylabel('ADC Value')
plt.grid(1)
plt.legend()
plt.savefig('waveform_plot.png', dpi=300, bbox_inches='tight')
plt.close()



# Plot CSV Graph
with open('ADC_Value.csv', mode='w', newline='') as file:
    writer = csv.writer(file)

    # first row indicates the sample rate
    writer.writerow(['Sampling Rate is', SAMPLE_RATE])

    # write the ADC value for every row
    for val in amplitude_list:
        writer.writerow([val])

print("CSV file saved as 'ADC_Value.csv'")





print("\n")
file.close()
ser.close()
compileResult = subprocess.getstatusoutput(f"gcc read_serial.c -o read_serial")
codeOutput = subprocess.getstatusoutput(f"read_serial 2outlier_ADC_values.data 2outlier.wav") #runs the executable with command line arguments
print(compileResult[0]) #prints 0 if compiled with no issues
print(compileResult[1]) #prints compilation errors, if any
print(codeOutput[0]) #prints 0 if the C program could run without any errors
print(codeOutput[1]) #prints any output displayed onto the terminal by the C program