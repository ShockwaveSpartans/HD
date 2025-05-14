import serial
import numpy as np
import sys, subprocess, time, os
import matplotlib.pyplot as plt
import csv


amplitude_list = []
try:
    while (True):
        ser = serial.Serial(port="COM10", baudrate = 921600, bytesize=8, parity="N", stopbits=1, timeout=5)
        datafile = "57new_ADC_values.data"
        wavfile = "57new.wav"
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
            ser.write(b'1')                 # Enter distance trigger mode
            time.sleep(0.5)                 # Let STM32 process

            print("\n\n")
            print("====================================================================")
            print("Data sampling starting...")
            print("====================================================================")
            print("\n\n")

            # Configuration
            CHUNK_SIZE = 500         # Size of each read
            SAMPLE_RATE = 10000
            music_length = time_input #the wav file will be time input * 2 second
            TOTAL_BYTES = music_length * SAMPLE_RATE 
            #TOTAL_BYTES = 100 * 1024  

            #amplitude_list = []


            # Open binary file for writing raw ADC data
            with open(datafile, "ab") as file:
                bytes_read = 0
                while bytes_read < TOTAL_BYTES:
                    # read in chunk size
                    chunk = ser.read(CHUNK_SIZE)
                    #check if there is data receive
                    if not chunk:  
                        print("\n No data received.")
                        break
                    file.write(chunk)             # Write to file

                    # check the total byte size received
                    bytes_read += len(chunk)
                    print(f"{bytes_read}/{TOTAL_BYTES} bytes received...", end='\r')
            
            # Close serial port
            ser.close()
            print("\n\n\n")
            print("====================================================================")
            print("Data sampling complete.")
            print("====================================================================")



        ################ distance ################
        if user_input == 2:
            print("====================================================================")
            print("You have selected Distance Trigger Mode ")
            print("====================================================================")

            time.sleep(0.5)
            ser.write(b'2')                 # Enter distance trigger mode
            time.sleep(0.5)                  # Let STM32 process

            print("\n\n")
            print("====================================================================")
            print("Data sampling starting...")
            print("====================================================================")
            print("\n\n")

            # Configuration
            CHUNK_SIZE = 2         # Size of each read
            #SAMPLE_RATE = 10000
            # music_length = time_input * 2   #the wav file will be time input * 2 second
            # TOTAL_BYTES = music_length * SAMPLE_RATE 
            #TOTAL_BYTES = 100 * 1024  
            TIMEOUT_THRESHOLD = 2        # 1ms timeout (0.25 seconds)
            #amplitude_list = []
            

            # Open binary file for writing raw ADC data
            with open(datafile, "ab") as file:
                bytes_read = 0
                last_received_time = None
                start_time = time.time()
                
                while True:
                    chunk = ser.read(CHUNK_SIZE)
                    current_time = time.time()
                    
                    if chunk:
                        # Write data and update timestamp
                        file.write(chunk)
                        bytes_read += len(chunk)
                        last_received_time = current_time
                        print(f"[INFO] {bytes_read} bytes received...", end='\r')
                    else:
                        # Check timeout conditions
                        if last_received_time:  # Had previous data
                            if (current_time - last_received_time) > TIMEOUT_THRESHOLD:
                                print("\nNo data for 250ms - Stopping")
                                break
                        else:  # No data received yet
                            if (current_time - start_time) > TIMEOUT_THRESHOLD:
                                print("\nNo initial data - Check sensor")
                                break
            ser.close()
            print("\n\n\n")
            print("====================================================================")
            print("Data sampling complete.")
            print("====================================================================")






        # # Plot Graph
        half_samples = len(amplitude_list) // 2
        half_amplitude_list = amplitude_list[:half_samples]
        timing = np.linspace(0, time_input, len(half_amplitude_list))                # Time from 0 to input time (second)

        plt.figure(figsize=(10, 4))
        plt.plot(timing, half_amplitude_list, label='ADC Value')
        plt.title('Amplitude vs Time')
        plt.xlabel('Time (s)')
        plt.ylabel('ADC Value')
        plt.grid(1)
        plt.legend()
        plt.savefig('waveform_plot.png', dpi=300, bbox_inches='tight')
        plt.close()



        # # Plot CSV Graph
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
        compileResult = subprocess.getstatusoutput(f"gcc read_serial.c -o read_serial")
        codeOutput = subprocess.getstatusoutput(f"read_serial {datafile} {wavfile}") #runs the executable with command line arguments
        print(compileResult[0]) #prints 0 if compiled with no issues
        print(compileResult[1]) #prints compilation errors, if any
        print(codeOutput[0]) #prints 0 if the C program could run without any errors
        print(codeOutput[1]) #prints any output displayed onto the terminal by the C program

except KeyboardInterrupt:
    print("Program exiting...")