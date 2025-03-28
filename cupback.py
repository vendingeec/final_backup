import RPi.GPIO as GPIO
import time

# GPIO Pin for Pulse signal
PULSE_PIN = 6  # Connect to the Pulse pin of DM542
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
# Motor settings
STEPS_PER_REVOLUTION = 200  # Adjust based on your motor
CUP_DISPENSING_STEPS = 1200  # Steps required to dispense one cup
STEP_DELAY = 0.0005  # Delay between steps (adjust for speed)

def setup_motor():
      # Use BCM pin numbering
    GPIO.setup(PULSE_PIN, GPIO.OUT)

def rotate_motor(steps, delay):
    for _ in range(steps):
        GPIO.output(PULSE_PIN, GPIO.HIGH)
        time.sleep(delay)
        GPIO.output(PULSE_PIN, GPIO.LOW)
        time.sleep(delay)

def dispense_cup():
    try:
        setup_motor()
        rotate_motor(CUP_DISPENSING_STEPS, STEP_DELAY)
        print("Cup dispensed!")
    except KeyboardInterrupt:
        print("Program interrupted.")

if __name__ == "__main__":
    dispense_cup()
