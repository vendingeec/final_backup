#heating  pump test
import RPi.GPIO as GPIO
import time

# Define the GPIO pin for the water relay
WATER_RELAY_PIN = 12# Example GPIO pin for water relay
GPIO.setwarnings(False)
# Ensure GPIO is initialized correctly at the start
GPIO.setmode(GPIO.BCM)  # or GPIO.BOARD, depending on your configuration
print("GPIO initialized to BCM mode.")

# Function to setup GPIO for the water dispensing relay
def setup_water_relay():
    GPIO.setup(WATER_RELAY_PIN, GPIO.OUT)
    GPIO.output(WATER_RELAY_PIN, GPIO.HIGH)  # Default to off

# Function to dispense water based on quantity
def dispense_water(quantity):
    
    """
    Dispenses water based on the selected quantity.

    Parameters:
    quantity (int): Amount of water to dispense (200 or 400 ml).
    """
    try:
        
        print("Setting up water relay...")
        # Setup GPIO for the relay
        setup_water_relay()
        GPIO.output(WATER_RELAY_PIN, GPIO.LOW)

        # Determine the duration to run the pump
        if quantity == 200:
            duration = 1 # Relay on for 6.5 seconds for 200 ml
        elif quantity == 400:
            duration = 30  # Relay on for 13 seconds for 400 ml
        else:
            raise ValueError("Invalid water quantity. Choose either 200 ml or 400 ml.")

        # Activate the relay (turn on the water pump)
        print(f"Dispensing {quantity} ml of water...")  # Step 3 in main program
        GPIO.output(WATER_RELAY_PIN, GPIO.LOW)
        time.sleep(duration)  # Wait for the required time (to dispense water)
        GPIO.output(WATER_RELAY_PIN, GPIO.HIGH)  # Turn off the relay (stop the pump)
        print(f"Successfully dispensed {quantity} ml of water.")

    except Exception as e:
        print(f"Error dispensing water: {e}")


if __name__ == "__main__":
    print("Starting water dispensing program...")
    # Ask user for the quantity of water to dispense
    try:
        quantity = int(input("Enter quantity (200 or 400 ml): "))
        dispense_water(quantity)
    except ValueError:
        print("Invalid input. Please enter 200 or 400.")
