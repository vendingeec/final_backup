import RPi.GPIO as GPIO
import time

LIMIT_SWITCH_PIN = 18

GPIO.setmode(GPIO.BCM)
GPIO.setup(LIMIT_SWITCH_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Function to handle switch press event
def switch_pressed(channel):
    print("✅ Limit switch pressed!")

try:
    GPIO.add_event_detect(LIMIT_SWITCH_PIN, GPIO.FALLING, callback=switch_pressed)  # Removed bouncetime
except RuntimeError as e:
    print(f"Error: {e}")
    GPIO.cleanup()
    exit(1)

print("Waiting for limit switch press... (Press Ctrl+C to exit)")

try:
    while True:
        if GPIO.input(LIMIT_SWITCH_PIN) == GPIO.HIGH:
            print("❌ Limit switch released!")
        time.sleep(0.5)
except KeyboardInterrupt:
    print("\nExiting...")
    GPIO.cleanup()
