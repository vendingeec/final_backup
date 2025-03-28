import RPi.GPIO as GPIO
import time

# Define GPIO pin for the limit switch
LIMIT_SWITCH_PIN = 2

# Clean up GPIO settings before starting
GPIO.cleanup()

# Set up GPIO mode and input pin with a pull-up resistor
GPIO.setmode(GPIO.BCM)  
GPIO.setup(LIMIT_SWITCH_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  # Default LOW


print("Waiting for limit switch press... (Press Ctrl+C to exit)")

try:
    while True:
        if GPIO.input(LIMIT_SWITCH_PIN) == GPIO.LOW:
            print("✅ Limit switch pressed!")
        else:
            print("❌ Limit switch released!")

        time.sleep(0.1)  # Small delay to reduce CPU usage

except KeyboardInterrupt:
    print("\nExiting...")
    GPIO.cleanup()  # Clean up GPIO on exit
