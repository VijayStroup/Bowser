import serial
import time

ser = serial.Serial('/dev/ttyTHS1')
print(ser.name)
while True:
	ser.write(b'hello')
	time.sleep(.001)
ser.close()
