import RPi.GPIO as GPIO
import time

# Define GPIO pins for Motor 1
MOTOR1_PUL = 18  # Pulse pin for Motor 1
MOTOR1_DIR = 23  # Direction pin for Motor 1

# Define GPIO pins for Motor 2
MOTOR2_PUL = 24  # Pulse pin for Motor 2
MOTOR2_DIR = 25  # Direction pin for Motor 2

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(MOTOR1_PUL, GPIO.OUT)
GPIO.setup(MOTOR1_DIR, GPIO.OUT)
GPIO.setup(MOTOR2_PUL, GPIO.OUT)
GPIO.setup(MOTOR2_DIR, GPIO.OUT)

# Define common direction (Change this value to control both motors)
COMMON_DIRECTION = GPIO.LOW


  # Set to GPIO.LOW for reversepo

# Apply common direction to both motors
GPIO.output(MOTOR1_DIR, COMMON_DIRECTION)
GPIO.output(MOTOR2_DIR, COMMON_DIRECTION)

# Function to move both motors
def stepper_motors(steps, delay):
    for _ in range(steps):
        GPIO.output(MOTOR1_PUL, GPIO.HIGH)
        GPIO.output(MOTOR2_PUL, GPIO.HIGH)
        time.sleep(delay)  # Step delay (speed control)
        GPIO.output(MOTOR1_PUL, GPIO.LOW)
        GPIO.output(MOTOR2_PUL, GPIO.LOW)
        time.sleep(delay)

# Test motors
try:
    stepper_motors(200, 0.00025)  # Move motors with the defined common direction
except Exception as e:
    print(f"Error: {e}")
finally:
    GPIO.cleanup()  # Clean up GPIO
