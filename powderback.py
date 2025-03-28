import time
import RPi.GPIO as GPIO

# Set up Raspberry Pi GPIO pins
GPIO.setmode(GPIO.BCM)

# Define motor pins using Raspberry Pi GPIO pins (no need for MCP23017 anymore)
MOTOR_PINS = {
    "horizontal_1": {"pulse": 18, "direction": 23},  # Use GPIO pins for horizontal motor 1
    "horizontal_2": {"pulse": 24, "direction": 25},  # Use GPIO pins for horizontal motor 2
    "gantry": {"pulse": 26, "direction": 21}         # Use GPIO pins for gantry motor
}

# Set up GPIO pin modes (removed ENABLE_PIN)
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

def move_powder_stepper(motor_pins, steps):
    for step in range(steps):
        GPIO.output(motor_pins["pulse"], GPIO.HIGH)
        time.sleep(0.00025)
        GPIO.output(motor_pins["pulse"], GPIO.LOW)
        time.sleep(0.00025)

# Function to move gantry to a specific position
def move_gantry_to_position(flavor_position):
    gantry_steps = {
        1: (0, 0, 9500),
        2: (4000, 4000, 9000),
        3: (7800, 7800, 9000),
        4: (11500, 11500, 9000),
        5: (15500, 15500, 9000),
        6: (19500, 19500, 9000),
        7: (23600, 23600, 9000),
        8: (27900, 27900, 9000),
        9: (31400, 31400, 9000),
    }
    
    steps_motor_1, steps_motor_2, steps_motor_3 = gantry_steps.get(flavor_position, (0, 0, 0))

    # Set directions
    GPIO.output(MOTOR_PINS['horizontal_1']['direction'], True)  # Move forward (Clockwise)
    GPIO.output(MOTOR_PINS['horizontal_2']['direction'], True)  # Move forward (Clockwise)
    GPIO.output(MOTOR_PINS['gantry']['direction'], False)  # Move reverse (Counterclockwise)

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

# Function to dispense powder
def dispense_powder(flavor, qty):
    try:
        flavor_motor_pins = {
            1: {'pulse': 4},
            2: {'pulse': 17},
            3: {'pulse': 27},
            4: {'pulse': 22},
            5: {'pulse': 10},
            6: {'pulse': 9},
            7: {'pulse': 11},
            8: {'pulse': 0},
            9: {'pulse': 5},
        }

        if flavor not in flavor_motor_pins:
            raise ValueError("Invalid flavor selected, choose between 1 and 9.")

        motor_pins = flavor_motor_pins[flavor]

        GPIO.setup(motor_pins['pulse'], GPIO.OUT)

        if qty == 200:
            steps_per_revolution = 200
            stepper_rotations = 31
            powder_weight = 33
        elif qty == 400:
            steps_per_revolution = 200
            stepper_rotations = 90
            powder_weight = 100
        else:
            raise ValueError("Invalid quantity selected, must be 200ml or 400ml.")
        
        print(f"Dispensing {powder_weight} g of flavor {flavor}...")

        steps_to_dispense = steps_per_revolution * stepper_rotations

        move_powder_stepper(motor_pins, steps_to_dispense)

        print(f"{powder_weight}g of Flavor {flavor} powder dispensed.")
    
    except Exception as e:
        print(f"Error dispensing powder: {e}")

# Main program
def main():
    try:
        flavor = int(input("Enter the flavor number (1-9): "))
        qty = int(input("Enter the quantity (200 or 400 ml): "))

        #move_gantry_to_position(flavor)
        dispense_powder(flavor, qty)

    except Exception as e:
        print(f"Error in main program: {e}")
    finally:
        GPIO.cleanup()

if __name__ == "__main__":
    main()
