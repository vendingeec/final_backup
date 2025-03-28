import serial
from servo import move_servo_left, move_servo_right
import time
import RPi.GPIO as GPIO


# Blender control constants (example)
BLENDER_ON = 1  # Blender ON command
BLENDER_OFF = 0  # Blender OFF command

# Stepper motor control pins (example)
STEP_PIN = 13  # Stepper motor step pin
DIR_PIN = 19   # Stepper motor direction pin

# Relay control pin for the gear motor (GPIO 23)
RELAY_PIN = 7  # GPIO pin for controlling relay

# Setup GPIO (only once)
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(STEP_PIN, GPIO.OUT)
GPIO.setup(DIR_PIN, GPIO.OUT)
GPIO.setup(RELAY_PIN, GPIO.OUT)
GPIO.output(RELAY_PIN, GPIO.HIGH)   # Setup relay pin as output



# Function to control the gear motor (via relay)
def control_gear_motor(state):
    if state == BLENDER_ON:
        print("Gear motor ON (Relay Activated)")
        GPIO.output(RELAY_PIN, GPIO.LOW)  # Activate relay to turn on motor (active-low)
    else:
        print("Gear motor OFF (Relay Deactivated)")
        GPIO.output(RELAY_PIN, GPIO.HIGH)  # Deactivate relay to turn off motor
    time.sleep(0.5)  # Allow time for the motor driver to react

# Function to move stepper motor
def move_stepper(steps, direction):
    GPIO.output(DIR_PIN, direction)  # Set direction
    for _ in range(steps):
        GPIO.output(STEP_PIN, GPIO.HIGH)
        time.sleep(0.001)  # Adjust speed here
        GPIO.output(STEP_PIN, GPIO.LOW)
        time.sleep(0.001)  # Adjust speed here

# Function to move blender to blending position
def move_to_blend_position():
    ser = serial.Serial('/dev/serial0', baudrate=115200, timeout=1)
    print("Moving servo to Blending Position.")
    move_servo_left(ser)  # Move to left position
    time.sleep(0.5)

    print("Moving stepper motor down.")
    move_stepper(1700, GPIO.HIGH)  # Move down (forward)
    time.sleep(0.5)

# Function for the blending process
def blending_process(quantity):
    oscillation_cycles = 5 if quantity == 200 else 10  # Set cycles based on quantity
    oscillation_steps = 300 if quantity == 200 else 300  # Set steps based on quantity

    print("Turning on gear motor for blending.")
    control_gear_motor(BLENDER_ON)  # Turn on gear motor

    print(f"Oscillating stepper motor while blending ({oscillation_cycles} cycles).")
    for _ in range(oscillation_cycles):  # Oscillate based on quantity
        move_stepper(oscillation_steps, GPIO.HIGH)  # Move forward
        time.sleep(0.5)
        move_stepper(oscillation_steps, GPIO.LOW)   # Move reverse
        time.sleep(0.5)

    print("Turning off gear motor after blending.")
    control_gear_motor(BLENDER_OFF)  # Turn off gear motor
    time.sleep(0.5)

# Function to return blender to home position
def move_to_home_position():
    ser = serial.Serial('/dev/serial0', baudrate=115200, timeout=1)
    print("Moving stepper motor up.")
    move_stepper(1700, GPIO.LOW)  # Move up (reverse)
    time.sleep(0.5)

    print("Moving servo to Home Position.")
    move_servo_right(ser)  # Move servo to home position
    time.sleep(0.5)

    print("Program completed successfully.")

# Function to simulate washing operation
def washing_operation():
    ser = serial.Serial('/dev/serial0', baudrate=115200, timeout=1)
    print("Starting washing operation.")
    move_servo_right(ser)  # Move servo to home position
    time.sleep(0.5)
    # Move stepper motor forward for washing
    print("Moving stepper motor forward for washing.")
    move_stepper(1400, GPIO.HIGH)  # Move forward for washing
    time.sleep(0.5)

    # Turn on gear motor for washing
    print("Turning on gear motor for washing.")
    control_gear_motor(BLENDER_ON)  # Turn on gear motor for washing
    time.sleep(10)  # Wash for 10 seconds

    # Turn off gear motor after washing
    print("Turning off gear motor after washing.")
    control_gear_motor(BLENDER_OFF)  # Turn off gear motor
    time.sleep(0.5)

    # Move stepper motor up after washing
    print("Moving stepper motor up after washing.")
    move_stepper(1400, GPIO.LOW)  # Move up (reverse)
    time.sleep(0.5)

    # Return servo to HOME POSITION
    print("Servo in Home Position.")
    move_servo_right(ser)
    print("Washing operation completed.")

# Main function
if __name__ == "__main__":
    
    # Ask the user for the quantity
    try:
        quantity = int(input("Enter the quantity (200 or 400): "))  # Get the quantity (200 or 400)

        if quantity not in [200, 400]:
            print("Invalid quantity. Please enter either 200 or 400.")
        else:
            ser = serial.Serial('/dev/serial0', baudrate=115200, timeout=1)
            moving_steps = 1700  # Same for both 200ml and 400ml

            move_to_blend_position()
            blending_process(quantity)
            move_to_home_position()
            washing_operation()

    except ValueError:
        print("Invalid input. Please enter a valid number (200 or 400).")
