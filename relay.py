import RPi.GPIO as GPIO

RELAY_PIN = 8 # Change this to your actual GPIO pin

GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY_PIN, GPIO.OUT, initial=GPIO.HIGH)  # Set relay HIGH at boot
