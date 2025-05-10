import serial
import sys, subprocess, time, os

print("\n")
print("====================================================================")
print("Welcome to the main menu")
print("\nPlease choose a operating mode:")
print("\n1. Manual Recording Mode")
print("\n2. Distance Trigger Mode")
print("====================================================================")
print("\n")

userInput = 0
userInput = int(input())

if (userInput == 1):
    userTime = 0
    userTime = int(input("\nSeconds: \n"))

    # Configuration
    CHUNK_SIZE = 2        # Size of each read
    SAMPLE_RATE = 6400
    TIME = userTime 
    #the wav file will be 5 second
    TOTAL_BYTES = TIME * SAMPLE_RATE *CHUNK_SIZE
    #TOTAL_BYTES = 100 * 1024  

    # Open serial port
    ser = serial.Serial(port="COM11", baudrate = 230400, bytesize=8, parity="N", stopbits=1, timeout=5)

    print(f"[INFO] Serial port opened: {ser.name}")
    ### send a flag for adc (FLAG= HUART2 RECEIVE)
    ser.write(b'1')  
    time.sleep(0.1)
    ###
    # Open binary file for writing raw ADC data
    with open("Transfer_ADC_values.data", "ab") as file:
        bytes_read = 0
        while bytes_read < TOTAL_BYTES: #38400 byte for
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

if (userInput == 2):
    # Configuration
    CHUNK_SIZE = 2                  # Match STM32's 2-byte samples
    TIMEOUT_THRESHOLD = 1        # 250ms timeout (0.25 seconds)
    
    ser = serial.Serial(port="COM11", baudrate = 230400, bytesize=8, parity="N", stopbits=1, timeout=2)

    print(f"[INFO] Serial port opened: {ser.name}")
    ser.write(b'2')                 # Enter distance trigger mode
    time.sleep(0.1)                 # Let STM32 process
    
    with open("Transfer_ADC_values.data", "ab") as file:
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
    # Continue with WAV file creation...
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