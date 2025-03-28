import RPi.GPIO as GPIO
import time
GPIO.setwarnings(False)
# GPIO pin assignments
SOLENOID_VALVE_PIN = 12# GPIO pin for solenoid valve relay
PUMP_PIN = 1           # GPIO pin for pump relay
TEMPERATURE_MODULE_PIN = 16  # GPIO pin for temperature module relay

# Time durations (in seconds)
DRAIN_DURATION = 1# Time to keep the solenoid valve open for draining
FILL_DURATION = 120  # Time to keep the pump on for refilling

# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(SOLENOID_VALVE_PIN, GPIO.OUT)
GPIO.setup(PUMP_PIN, GPIO.OUT)
GPIO.setup(TEMPERATURE_MODULE_PIN, GPIO.OUT)
GPIO.output(PUMP_PIN, GPIO.HIGH) 
GPIO.output(SOLENOID_VALVE_PIN, GPIO.HIGH) 
GPIO.output(TEMPERATURE_MODULE_PIN, GPIO.LOW) 

# Function to control the solenoid valve
def control_solenoid(state):
    if state:
        print("Opening solenoid valve to drain water.")
        GPIO.output(SOLENOID_VALVE_PIN, GPIO.LOW)  # Activate solenoid valve
    else:
        print("Closing solenoid valve.")
        GPIO.output(SOLENOID_VALVE_PIN, GPIO.HIGH)   # Deactivate solenoid valve

# Function to control the pump
def control_pump(state):
    if state:
        print("Turning on pump to fill water.")
        GPIO.output(PUMP_PIN, GPIO.LOW)  # Activate pump
    else:
        print("Turning off pump.")
        GPIO.output(PUMP_PIN, GPIO.HIGH)   # Deactivate pump

# Function to control the temperature module
def control_temperature_module(state):
    if state:
        print("Turning on temperature module (closing relay).")
        GPIO.output(TEMPERATURE_MODULE_PIN, GPIO.LOW)  # Close relay, supply power
    else:
        print("Turning off temperature module (opening relay).")
        GPIO.output(TEMPERATURE_MODULE_PIN, GPIO.HIGH)   # Open relay, cut power

# Main function to change water
def change_washing_water():
    try:
        print("Starting water change process.")

        # # Step 1: Turn off the temperature module
        control_temperature_module(False)

        # Step 2: Drain the water
        control_solenoid(True)  # Open solenoid valve
        time.sleep(DRAIN_DURATION)  # Wait for the drain duration
        control_solenoid(False)  # Close solenoid valve

        # Step 3: Refill the container
        control_pump(True)  # Turn on pump
        time.sleep(FILL_DURATION)  # Wait for the fill duration
        control_pump(False)  # Turn off pump

        # Step 4: Turn on the temperature module
        control_temperature_module(True)

        print("Water change process completed.")

    except KeyboardInterrupt:
        print("Process interrupted.")


# This block ensures the script runs only if executed directly
if __name__ == "__main__":
    change_washing_water()
