import time
import RPi.GPIO as GPIO

GPIO.setwarnings(False)
# Use BCM GPIO numbering
GPIO.setmode(GPIO.BCM)

# Define motor control pins using Raspberry Pi GPIO
MOTOR_PINS = {
    "horizontal_1": {"pulse": 18, "direction": 23},  # Replace with actual GPIO pins
    "horizontal_2": {"pulse": 24, "direction": 25},  # Replace with actual GPIO pins
    "gantry": {"pulse": 26, "direction": 21},        # Replace with actual GPIO pins
}

# Set up GPIO pin modes
for motor in MOTOR_PINS.values():
    GPIO.setup(motor["pulse"], GPIO.OUT)
    GPIO.setup(motor["direction"], GPIO.OUT)

# Function to move the motors
def move_stepper(motor_pins, steps, direction):
    GPIO.output(motor_pins["direction"], direction)  # Set direction

    for _ in range(steps):
        GPIO.output(motor_pins["pulse"], True)
        time.sleep(0.00025)  # Pulse ON time
        GPIO.output(motor_pins["pulse"], False)
        time.sleep(0.00025)  # Pulse OFF time

# Function to move the gantry to a specific position
def move_gantry_to_position_blender(flavor_position):
    gantry_steps = {
        1: (37900, 37900, 9800),
        2: (33900, 33900, 9900),
        3: (30100, 30100, 9900),
        4: (26350, 26350, 9900),
        5: (22400, 22400, 9900),
        6: (18350, 18350, 9900),
        7: (14300, 14300, 9900),
        8: (10000, 10000, 9900),
        9: (6500, 6500, 9900),
    }

    steps_motor_1, steps_motor_2, steps_motor_3 = gantry_steps.get(flavor_position, (0, 0, 0))

    # Set directions
    GPIO.output(MOTOR_PINS['horizontal_1']['direction'], steps_motor_1 > 0)
    GPIO.output(MOTOR_PINS['horizontal_2']['direction'], steps_motor_2 > 0)
    GPIO.output(MOTOR_PINS['gantry']['direction'], steps_motor_3 > 0)

    # Move gantry motor first if flavor = 8 or 9
    if flavor_position in [8, 9]:
        for _ in range(abs(steps_motor_3)):
            GPIO.output(MOTOR_PINS['gantry']['pulse'], True)
            time.sleep(0.00025)
            GPIO.output(MOTOR_PINS['gantry']['pulse'], False)
            time.sleep(0.00025)

        for step in range(max(abs(steps_motor_1), abs(steps_motor_2))):
            if step < abs(steps_motor_1):
                GPIO.output(MOTOR_PINS['horizontal_1']['pulse'], True)
            if step < abs(steps_motor_2):
                GPIO.output(MOTOR_PINS['horizontal_2']['pulse'], True)
            time.sleep(0.00025)
            GPIO.output(MOTOR_PINS['horizontal_1']['pulse'], False)
            GPIO.output(MOTOR_PINS['horizontal_2']['pulse'], False)
            time.sleep(0.00025)

    else:
        for step in range(max(abs(steps_motor_1), abs(steps_motor_2), abs(steps_motor_3))):
            if step < abs(steps_motor_1):
                GPIO.output(MOTOR_PINS['horizontal_1']['pulse'], True)
            if step < abs(steps_motor_2):
                GPIO.output(MOTOR_PINS['horizontal_2']['pulse'], True)
            if step < abs(steps_motor_3):
                GPIO.output(MOTOR_PINS['gantry']['pulse'], True)
            time.sleep(0.00025)
            GPIO.output(MOTOR_PINS['horizontal_1']['pulse'], False)
            GPIO.output(MOTOR_PINS['horizontal_2']['pulse'], False)
            GPIO.output(MOTOR_PINS['gantry']['pulse'], False)
            time.sleep(0.00025)

# Main execution
if __name__ == "__main__":
    try:
        flavor = int(input("Enter the flavor number (1-9): "))
        qty = int(input("Enter the quantity (200 or 400 ml): "))

        move_gantry_to_position_blender(flavor)

    except KeyboardInterrupt:
        print("Program interrupted.")
    finally:
        GPIO.cleanup()
        print("GPIO cleaned up. Program exited.")
