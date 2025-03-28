import RPi.GPIO as GPIO
import time

# Define GPIO pins for Motor 1
MOTOR1_PUL = 26  # Pulse pin for Motor 1
MOTOR1_DIR = 21# Direction pin for Motor 1

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(MOTOR1_PUL, GPIO.OUT)
GPIO.setup(MOTOR1_DIR, GPIO.OUT)

# Set motor direction (Change to GPIO.LOW for reverse)
GPIO.output(MOTOR1_DIR, GPIO.HIGH)

# Function to move the stepper motor
def stepper_motor(steps, delay):
    for _ in range(steps):
        GPIO.output(MOTOR1_PUL, GPIO.HIGH)
        time.sleep(delay)  # Step delay (speed control)
        GPIO.output(MOTOR1_PUL, GPIO.LOW)
        time.sleep(delay)

# Test motor
try:
    stepper_motor(10, 0.00025)  # Move motor 1
except Exception as e:
    print(f"Error: {e}")
finally:
    GPIO.cleanup()  # Clean up GPIO
