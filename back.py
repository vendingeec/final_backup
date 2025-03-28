import time
import RPi.GPIO as GPIO
import threading  # Only for the washing operation; no full threading for everything else
import os
# Import motor control functions
from cupback import dispense_cup
from waterback import dispense_water
from powderback import dispense_powder, move_gantry_to_position
from blenderback import move_gantry_to_position_blender
from blendermechanism import move_to_blend_position,blending_process,move_to_home_position,washing_operation
from washingcontainer import change_washing_water
from proximity import ensure_cup_taken,check_user_cup_option


# Ensure GPIO mode is set only once
if not GPIO.getmode():
    GPIO.setmode(GPIO.BCM)  # Using Broadcom pin numbering

GPIO.setwarnings(False)




# Define GPIO Pins for Stepper Motors
MOTOR_PINS = {
    "horizontal_1": {"pulse": 18, "direction": 23},  # Define actual GPIO pins
    "horizontal_2": {"pulse": 24, "direction": 25},
    "gantry": {"pulse": 26, "direction": 21}
}

# File to store order count
ORDER_COUNT_FILE = "/home/vendingmachine/RP/order_count.txt"
MAX_ORDERS_BEFORE_WATER_CHANGE = 20  # Change water after 20 orders



def update_gantry_status(step_message):
    """Update the gantry status file with the latest step message."""
    with open("/home/vendingmachine/RP/gantry_status.txt", "w") as file:
        file.write(step_message + "\n")


def save_blender_position(position):
    with open("/home/vendingmachine/RP/blender_status.txt", "w") as file:
        file.write(position+ "\n")
# Set up GPIO pins
for motor in MOTOR_PINS.values():
    GPIO.setup(motor["pulse"], GPIO.OUT)
    GPIO.setup(motor["direction"], GPIO.OUT)

# Function to pulse the motor
def pulse_motor(motor_pins, steps, direction):
    GPIO.output(motor_pins["direction"], GPIO.HIGH if direction == 'forward' else GPIO.LOW)

    for step in range(steps):
        GPIO.output(motor_pins["pulse"], GPIO.HIGH)
        time.sleep(0.000025)
        GPIO.output(motor_pins["pulse"], GPIO.LOW)
        time.sleep(0.00025)

# Move horizontal motors synchronously
def move_horizontal_synchronously(motor_pins_1, motor_pins_2, steps, direction):
    GPIO.output(motor_pins_1["direction"], GPIO.HIGH if direction == 'forward' else GPIO.LOW)
    GPIO.output(motor_pins_2["direction"], GPIO.HIGH if direction == 'forward' else GPIO.LOW)

    for step in range(steps):
        GPIO.output(motor_pins_1["pulse"], GPIO.HIGH)
        GPIO.output(motor_pins_2["pulse"], GPIO.HIGH)
        time.sleep(0.00025)
        GPIO.output(motor_pins_1["pulse"], GPIO.LOW)
        GPIO.output(motor_pins_2["pulse"], GPIO.LOW)
        time.sleep(0.00025)

# Move three motors synchronously
def move_three_motors_synchronously(motor_pins_1, motor_pins_2, motor_pins_3, steps_1, steps_2, steps_3, direction):
    GPIO.output(motor_pins_1["direction"], GPIO.HIGH if direction == 'forward' else GPIO.LOW)
    GPIO.output(motor_pins_2["direction"], GPIO.HIGH if direction == 'forward' else GPIO.LOW)
    GPIO.output(motor_pins_3["direction"], GPIO.HIGH if direction == 'forward' else GPIO.LOW)

    for step in range(max(steps_1, steps_2, steps_3)):
        if step < steps_1:
            GPIO.output(motor_pins_1["pulse"], GPIO.HIGH)
        if step < steps_2:
            GPIO.output(motor_pins_2["pulse"], GPIO.HIGH)
        if step < steps_3:
            GPIO.output(motor_pins_3["pulse"], GPIO.HIGH)

        time.sleep(0.00025)

        if step < steps_1:
            GPIO.output(motor_pins_1["pulse"], GPIO.LOW)
        if step < steps_2:
            GPIO.output(motor_pins_2["pulse"], GPIO.LOW)
        if step < steps_3:
            GPIO.output(motor_pins_3["pulse"], GPIO.LOW)

        time.sleep(0.00025)

# Move single stepper motor
def move_stepper(motor_pins, steps, direction):
    GPIO.output(motor_pins["direction"], GPIO.HIGH if direction == 'forward' else GPIO.LOW)

    for step in range(steps):
        GPIO.output(motor_pins["pulse"], GPIO.HIGH)
        time.sleep(0.00025)
        GPIO.output(motor_pins["pulse"], GPIO.LOW)
        time.sleep(0.00025)

# Function to load order count from file
def load_order_count():
    if os.path.exists(ORDER_COUNT_FILE):
        with open(ORDER_COUNT_FILE, "r") as file:
            try:
                return int(file.read().strip())  # Read and convert to int
            except ValueError:
                return 0  # Reset if file is corrupted
    return 0  # Default if file does not exist

# Function to save order count to file
def save_order_count(order_count):
    with open(ORDER_COUNT_FILE, "w") as file:
        file.write(str(order_count))

def oscillate_motors(steps=9):
     

    print("""Oscillates the three motors back and forth for the given cycle.""")
    for _ in range(steps):
        move_three_motors_synchronously(
            MOTOR_PINS["horizontal_1"], MOTOR_PINS["horizontal_2"], MOTOR_PINS["gantry"],
            100, 100, 100, "forward"
        )
        time.sleep(0.1)  # Small delay for motor stabilization

        move_three_motors_synchronously(
            MOTOR_PINS["horizontal_1"], MOTOR_PINS["horizontal_2"], MOTOR_PINS["gantry"],
            100, 100, 100, "backward"
        )
        time.sleep(0.1)  # Small delay for motor stabilization

def blending_process_with_oscillation(water_quantity):
    """
    This function starts the blending process and ensures oscillate_motors()
    runs continuously until blending is finished.
    """
    global blending_active
    blending_active = True  # Set flag to indicate blending is in progress

    # Start oscillating motors in a separate thread
    oscillation_thread = threading.Thread(target=oscillate_motors_while_blending)
    oscillation_thread.start()

    # Run blending process
    blending_process(water_quantity)  # Turns ON gear motor and blends

    # Once blending is done, stop the oscillation
    blending_active = False
    oscillation_thread.join()  # Wait for oscillation to finish


def oscillate_motors_while_blending():
    """
    This function continuously oscillates motors while blending_active is True.
    It stops when blending_active is set to False.
    """
    while blending_active:
        oscillate_motors()
        time.sleep(0.5)  # Small delay to control loop speed

# Load the order count when script starts
order_count = load_order_count()

# Function to process an order
def process_order():
    global order_count

    while True:  
        cup_type = input("Enter cup type (machine/user): ").strip().lower()
        while cup_type not in ['machine', 'user']:
            print("Invalid input. Please enter 'machine' or 'user'.")
            cup_type = input("Enter cup type (machine/user): ").strip().lower()

        try:
            flavor = int(input("Enter flavor (1-9): "))
            while flavor not in range(1, 10):
                print("Invalid flavor. Please enter a number between 1 and 9.")
                flavor = int(input("Enter flavor (1-9): "))
        except ValueError:
            print("Invalid input. Please enter a number between 1 and 9.")
            continue

        try:
            water_quantity = int(input("Enter water quantity (200 or 400): "))
            while water_quantity not in [200, 400]:
                print("Invalid water quantity. Please enter 200 or 400.")
                water_quantity = int(input("Enter water quantity (200 or 400): "))
        except ValueError:
            print("Invalid input. Please enter 200 or 400.")
            continue

        print(f"\nProcessing order: Cup Type: {cup_type}, Flavor: {flavor}, Water Quantity: {water_quantity} ml\n")

        try:

             # Step 1: Move to home position
            print("Step 1: At home position (Cup Dispensing Station)...")
            move_horizontal_synchronously(
                MOTOR_PINS["horizontal_1"], MOTOR_PINS["horizontal_2"], 0, "reverse")
            move_stepper(MOTOR_PINS["gantry"], 0, "reverse")
            time.sleep(0.5)

            update_gantry_status("Cup Station")

            if cup_type == "machine":
                print("Step 2: Dispensing cup...")
                dispense_cup()
            else:
                print("Step 2: Moving to delivery point for user cup...")
                move_horizontal_synchronously(
                    MOTOR_PINS["horizontal_1"], MOTOR_PINS["horizontal_2"], 35000, "forward")
                move_stepper(MOTOR_PINS["gantry"], 1500, "forward")
                print("Please place your cup in the designated area.")

                check_user_cup_option()

                print("User cup detected.")

            update_gantry_status("Water Station")

            if cup_type == "machine":
                update_gantry_status("Water Station")
                # For machine cup: move to water dispensing station with specific steps
                print("Step 3: Moving to water dispensing station for machine cup...")
                move_stepper(MOTOR_PINS["gantry"], 10500, "reverse")
                time.sleep(0.2)
                move_horizontal_synchronously(
                    MOTOR_PINS["horizontal_1"], MOTOR_PINS["horizontal_2"], 7000, "reverse")
            else:
                update_gantry_status("User Water Station")
                # For user cup: move to water dispensing station with different steps and direction
                print("Step 3: Moving to water dispensing station for user cup...")
                move_three_motors_synchronously(
                    MOTOR_PINS["horizontal_1"], MOTOR_PINS["horizontal_2"], MOTOR_PINS["gantry"], 41850, 41850, 10000, "reverse")

            # Call the function to dispense the water after moving to the dispensing station
            #dispense_water(water_quantity)
            time.sleep(0.5)

            update_gantry_status(F"Flavour {flavor}")
             # Step 4: Move to powder dispensing station
            print("Step 4: Moving to powder dispensing station...")
            move_gantry_to_position(flavor)
            dispense_powder(flavor, water_quantity)
            time.sleep(0.5)
            

            
            update_gantry_status("Blender Station")

            print("Step 5: Moving to blender station...")
            move_gantry_to_position_blender(flavor)
            time.sleep(1)

            # Move to the blending position
            save_blender_position("blender")
            move_to_blend_position()
            # save_blender_position("blender")
            

            blending_process_with_oscillation(water_quantity)

            # Move back to home after blending
            move_to_home_position()
            save_blender_position("home")

        

            update_gantry_status("Deivery Station")

            print("Step 6: Moving to delivery point...")
            washing_thread = threading.Thread(target=washing_operation)
            washing_thread.start()  # Start washing operation in the background

            move_stepper(MOTOR_PINS["gantry"], 10500, "forward")
            move_horizontal_synchronously(
                    MOTOR_PINS["horizontal_1"], MOTOR_PINS["horizontal_2"], 3950, "forward")

            
            ensure_cup_taken()

            print("Step 7: Returning to home position (Cup Dispensing Station)...")
            move_three_motors_synchronously(
                MOTOR_PINS["horizontal_1"], MOTOR_PINS["horizontal_2"], MOTOR_PINS["gantry"], 34900, 34900, 7900, "reverse")
            move_stepper(MOTOR_PINS["gantry"], 7500, "forward")

            print("Process complete")

            update_gantry_status("home")

            order_count += 1  
            save_order_count(order_count)  
            print(f"Order {order_count} completed.")

            if order_count % MAX_ORDERS_BEFORE_WATER_CHANGE == 0:
                print(f"{MAX_ORDERS_BEFORE_WATER_CHANGE} orders completed. Changing washing water...")
                change_washing_water()
                order_count = 0  
                save_order_count(order_count)

        except Exception as e:
            print(f"Error occurred: {str(e)}")

        another_order = input("Would you like to place another order? (yes/no): ").strip().lower()
        if another_order == 'no':
            print("Thank you for using the vending machine!")
            break  

if __name__ == "__main__":
    process_order()
