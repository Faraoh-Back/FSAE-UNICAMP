import serial
import RPi.GPIO as GPIO
import time

SERIAL_PORT = "/dev/serial0"
BAUDRATE = 9600

PIN_M0 = 17
PIN_M1 = 18
PIN_AUX = 27

GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN_M0, GPIO.OUT)
GPIO.setup(PIN_M1, GPIO.OUT)
GPIO.setup(PIN_AUX, GPIO.IN)

# Coloca E22 em modo normal
GPIO.output(PIN_M0, GPIO.LOW)
GPIO.output(PIN_M1, GPIO.LOW)
time.sleep(0.1)

ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1)
print("Aguardando mensagens LoRa...")

try:
    while True:
        if ser.in_waiting > 0:
            msg = ser.readline().decode('utf-8', errors='ignore').strip()
            print("Recebido:", msg)
except KeyboardInterrupt:
    print("Saindo.")
finally:
    ser.close()
    GPIO.cleanup()