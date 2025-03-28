import RPi.GPIO as GPIO
import time

SENSOR_PIN = 15  # GPIO 20

GPIO.setmode(GPIO.BCM)
GPIO.setup(SENSOR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  # Ensure pull-down

def check_user_cup_option():
    """
    Checks whether the user has placed a cup.
    Returns True if a cup is detected, otherwise False.
    """
    print("Waiting for user to place cup...")
    while True:
        if GPIO.input(SENSOR_PIN) == 1:  # Cup detected
            print("✅ Cup placed by user.")
            return True
        time.sleep(0.2)

def ensure_cup_taken():
    """
    Ensures the user has taken the cup before returning to the home position.
    Waits for the cup to be removed.
    """
    print("Waiting for user to take the cup...")
    while True:
        if GPIO.input(SENSOR_PIN) == 0:  # Cup removed
            print("✅ Cup taken by user. Returning to home position.")
            return True
        time.sleep(0.2)

if __name__ == "__main__":
    try:
        # Call the function explicitly only when the script is run directly
        if check_user_cup_option():
            print("Proceeding with the next operation...")

        print("Cup is at the delivery point.")

        if ensure_cup_taken():
            print("Moving to home position.")

    except KeyboardInterrupt:
        print("\nExiting Program")
