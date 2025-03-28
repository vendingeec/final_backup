import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setup(26, GPIO.OUT)

GPIO.output(26, GPIO.HIGH)  # Turn on
time.sleep(2)
GPIO.output(26, GPIO.LOW)   # Turn off

GPIO.cleanup()
