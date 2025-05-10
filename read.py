import serial
import time
import numpy as np
import wave

sampleRate = 6400  # bytes per second
recordTime = 15      # seconds

ser = serial.Serial(port="/dev/tty.usbmodem103", baudrate=230400, bytesize=8, parity="N", stopbits=1, timeout=5)
print(ser.name)

data = []
data2 = []

num_bytes_to_read = sampleRate * recordTime

f = open("raw_data.txt", "w")

for i in range(num_bytes_to_read):
    byte = ser.read(2) # transmit two bytes, 12 bits
    if byte:
        result = int(str(byte[0]) + str(byte[1]))
        data.append(result) # result will not be larger than 4095 or lesser than 0
        f.write(f"{result}\n")

f.close()

data = np.array(data)


data = data / 4095  # scale 12-bit range to [0, 1]
print(data)

data = (data * 2 - 1) * 32767  # Scale to [-32767, 32767]    
# Scale to [-32767, 32767]

data = data.astype(np.uint16)
print(data)

wav_file = wave.open("raw_ADC_values.wav","wb")
wav_file.setnchannels(1)
wav_file.setsampwidth(2)
wav_file.setframerate(sampleRate)
wav_file.writeframes(data.tobytes())
wav_file.close()


print(f"Recorded {len(data)} bytes in {recordTime} seconds.")

ser.close()
print(f"Created raw_data.txt with {num_bytes_to_read} samples.")