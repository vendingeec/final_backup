import RPi.GPIO as GPIO
import time
from servo import move_servo_right  # Import servo function
import sys
import serial
import pytz
from datetime import datetime
from proximity import ensure_cup_taken
from back import move_three_motors_synchronously
from time import sleep

log_file_path = "/home/vendingmachine/RP/startup.log"

# Redirect stdout and stderr to log file
sys.stdout = open(log_file_path, "a")
sys.stderr = open(log_file_path, "a")

def log_message(message):
    ist = pytz.timezone("Asia/Kolkata")  # Set timezone to IST
    timestamp = datetime.now(ist).strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}\n"
    
    try:
        with open("/home/vendingmachine/RP/startup.log", "a") as log_file:
            log_file.write(log_entry)
    except PermissionError:
        print("Permission denied: Unable to write to log file.")

# Define motor pins (note: no "enable" pin specified)
MOTOR_PINS = {
    "blender_stepper": {"pulse": 13, "direction": 19},
    "horizontal_1": {"pulse": 18, "direction": 23},
    "horizontal_2": {"pulse": 24, "direction": 25},
    "gantry": {"pulse": 26, "direction": 21},
}

# Define limit switch pins
LIMIT_SWITCHES = {
    "horizontal": 3,
    "gantry": 2
}

# GPIO Setup
GPIO.setmode(GPIO.BCM)

for motor in MOTOR_PINS.values():
    GPIO.setup(motor["pulse"], GPIO.OUT)
    GPIO.setup(motor["direction"], GPIO.OUT)

for switch in LIMIT_SWITCHES.values():
    GPIO.setup(switch, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Function to move a motor stepper a certain number of steps
def move_stepper(motor_pins, steps, direction):
    GPIO.output(motor_pins["direction"], GPIO.HIGH if direction == 'forward' else GPIO.LOW)
    for _ in range(steps):
        GPIO.output(motor_pins["pulse"], GPIO.HIGH)
        time.sleep(0.00025)
        GPIO.output(motor_pins["pulse"], GPIO.LOW)
        time.sleep(0.00025)
    print(f"Stepper moved {steps} steps {direction}")

# Function to move the blender stepper motor
def move_blender_stepper(motor_pins, steps, direction):
    GPIO.output(motor_pins["direction"], GPIO.HIGH if direction == 'forward' else GPIO.LOW)
    for _ in range(steps):
        GPIO.output(motor_pins["pulse"], GPIO.HIGH)
        time.sleep(0.001)
        GPIO.output(motor_pins["pulse"], GPIO.LOW)
        time.sleep(0.001)
    print(f"Stepper moved {steps} steps {direction}")

# Function to move a motor until a limit switch is reached
def move_until_limit(motor_pins, direction, limit_switch):
    # Set the direction based on the desired movement
    GPIO.output(motor_pins["direction"], GPIO.LOW if direction == "reverse" else GPIO.HIGH)
    while GPIO.input(limit_switch) == GPIO.HIGH:
        GPIO.output(motor_pins["pulse"], GPIO.HIGH)
        time.sleep(0.00025)
        GPIO.output(motor_pins["pulse"], GPIO.LOW)
        time.sleep(0.00025)
    print("Motor stopped at limit switch.")

# Move all three motors synchronously until one of the limit switches is triggered.
# Replacing the previous stop_motor and move_motor functions with inline pulse actions.
def move_three_motors_until_limits(motor_1, motor_2, motor_3, direction, limit_1, limit_2, limit_3):
    GPIO.output(motor_1["direction"], GPIO.HIGH if direction == 'forward' else GPIO.LOW)
    GPIO.output(motor_2["direction"], GPIO.HIGH if direction == 'forward' else GPIO.LOW)
    GPIO.output(motor_3["direction"], GPIO.HIGH if direction == 'forward' else GPIO.LOW)

    while (GPIO.input(limit_1) == GPIO.HIGH or GPIO.input(limit_2) == GPIO.HIGH or GPIO.input(limit_3) == GPIO.HIGH):
        if GPIO.input(limit_1) == GPIO.HIGH:
            GPIO.output(motor_1["pulse"], GPIO.HIGH)
        if GPIO.input(limit_2) == GPIO.HIGH:
            GPIO.output(motor_2["pulse"], GPIO.HIGH)
        if GPIO.input(limit_3) == GPIO.HIGH:
            GPIO.output(motor_3["pulse"], GPIO.HIGH)

        time.sleep(0.00025)

        GPIO.output(motor_1["pulse"], GPIO.LOW)
        GPIO.output(motor_2["pulse"], GPIO.LOW)
        GPIO.output(motor_3["pulse"], GPIO.LOW)

        time.sleep(0.00025)

    print("All three motors stopped at limit switches.")

# Function to read the blender position from file
def get_blender_position():
    try:
        with open("/home/vendingmachine/RP/blender_status.txt", "r") as file:
            return file.read().strip()
    except FileNotFoundError:
        return None

# Function to read the last known gantry position from file
def get_gantry_position():
    try:
        with open("/home/vendingmachine/RP/gantry_status.txt", "r") as file:
            return file.read().strip()
    except FileNotFoundError:
        return None

# Function to save the blender position to file
def save_blender_position(position):
    with open("/home/vendingmachine/RP/blender_status.txt", "w") as file:
        file.write(position)

# Function to save the gantry position to file
def save_gantry_position(position):
    with open("/home/vendingmachine/RP/gantry_status.txt", "w") as file:
        file.write(position)

# Restore system after power loss
def restore_after_power_cutoff():
    ser = serial.Serial('/dev/serial0', baudrate=115200, timeout=1)
    log_message("Restoring system after power loss...")
    print("Restoring system after power loss...")

    # Step 1: Handle blender position.
    blender_position = get_blender_position()
    print(f"Blender Position Read from File: {blender_position}")
    if blender_position == "home":
        print("Moving blender stepper motor 1550 steps in reverse...")
        move_blender_stepper(MOTOR_PINS["blender_stepper"], 1550, "reverse")
    elif blender_position == "blender":
        print("Moving blender stepper motor 2400 steps in reverse...")
        move_blender_stepper(MOTOR_PINS["blender_stepper"], 2400, "reverse")
        time.sleep(1)
        move_servo_right(ser)
    else:
        print("Unknown blender position, skipping movement.")

    # Save the blender position as home.
    save_blender_position("home")

    # Step 2: Handle gantry position.
    last_position = get_gantry_position()
    print(f"Gantry Position Read from File: {last_position}")
    if last_position == "home":
        print("Gantry is already at home position. No action needed.")
        return

    # Step 3: Move gantry based on the last position.
  # Step 3: Move gantry based on the last position.
    if last_position in ["Cup Station"]:
        print("Moving gantry motor 3000 steps in reverse...")
        move_stepper(MOTOR_PINS["gantry"], 5000, "reverse")

        print("Moving gantry and horizontal motors to home synchronously until limit switches are pressed...")
        move_three_motors_until_limits(
            MOTOR_PINS["gantry"], 
            MOTOR_PINS["horizontal_1"], 
            MOTOR_PINS["horizontal_2"], 
            "forward",
            LIMIT_SWITCHES["gantry"],
            LIMIT_SWITCHES["horizontal"],
            LIMIT_SWITCHES["horizontal"]
        )

    elif last_position in ["Water Station"]:
        print("Moving gantry motor forward until limit switch is pressed...")
        move_stepper(MOTOR_PINS["gantry"], 1000, "reverse")

        print("Moving horizontal motors forward until limit switch is pressed...")
        # Notice that here we use the same parameter ordering.
        move_three_motors_until_limits(
            MOTOR_PINS["gantry"], 
            MOTOR_PINS["horizontal_1"], 
            MOTOR_PINS["horizontal_2"], 
            "forward",
            LIMIT_SWITCHES["gantry"],
            LIMIT_SWITCHES["horizontal"],
            LIMIT_SWITCHES["horizontal"]
        )


    elif last_position in ["Flavour 8", "Flavour 9","Blender Station"]:
        print("Moving gantry motor forward until limit switch is pressed...")
        move_stepper(MOTOR_PINS["gantry"], 8000, "forward")

        print("Moving horizontal motors forward until limit switch is pressed...")
        # Notice that here we use the same parameter ordering.
        move_three_motors_until_limits(
            MOTOR_PINS["gantry"],
            MOTOR_PINS["horizontal_1"],
            MOTOR_PINS["horizontal_2"],
            "forward",
            LIMIT_SWITCHES["gantry"],
            LIMIT_SWITCHES["horizontal"],
            LIMIT_SWITCHES["horizontal"]
        )
    else:
        # Default movement if position is not specifically matched above.
        move_three_motors_until_limits(
            MOTOR_PINS["gantry"], 
            MOTOR_PINS["horizontal_1"], 
            MOTOR_PINS["horizontal_2"], 
            "forward",
            LIMIT_SWITCHES["gantry"],
            LIMIT_SWITCHES["horizontal"],
            LIMIT_SWITCHES["horizontal"]
        )

    print("System restored to delivery position.")
    save_gantry_position("home")

    # **Step 6: Ensure Faulty Cup is Taken**
    print("Step 6: Ensuring faulty cup is taken...")
    time.sleep(2)
    ensure_cup_taken()

    # **Step 7: Returning to Home Position (Cup Dispensing Station)**
    print("Step 7: Returning to home position (Cup Dispensing Station)...")
    move_three_motors_synchronously(
        MOTOR_PINS["horizontal_1"], MOTOR_PINS["horizontal_2"], MOTOR_PINS["gantry"], 
        34900, 34900, 7900, "reverse"
    )
    
    move_stepper(MOTOR_PINS["gantry"], 7500, "forward")
    print("System fully restored to Cup Dispensing Station.")

if __name__ == "__main__":
    # Run power recovery sequence
    restore_after_power_cutoff()
