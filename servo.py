import serial
import time

# Constants for servo positions
SERVO_ID = 1  # Default Servo ID
RIGHT_90_POSITION = 0
LEFT_90_POSITION = 500  

# Function to calculate checksum
def calculate_checksum(data):
    checksum = 0
    for byte in data[2:]:  # Skip header bytes
        checksum += byte
    checksum = ~checksum & 0xFF
    return checksum

# Function to send a position command to the servo
def move_servo(ser, position, move_time):
    position_l = position & 0xFF
    position_h = (position >> 8) & 0xFF
    time_l = move_time & 0xFF
    time_h = (move_time >> 8) & 0xFF

    # LX-224HV move command
    command = [
        0x55, 0x55,  # Header
        SERVO_ID,    # Servo ID
        7,           # Data length (7 bytes)
        1,           # Move command
        position_l, position_h, time_l, time_h,
        0            # Checksum (to be calculated)
    ]
    command[-1] = calculate_checksum(command)  # Calculate checksum

    ser.write(bytearray(command))  # Send command to servo
    time.sleep(0.1)  # Small delay for processing

# Function to move servo to Left 90° position
def move_servo_left(ser):
    print("Moving servo to Left 90° Position.")
    move_servo(ser, LEFT_90_POSITION, 1000)
    time.sleep(2)

# Function to move servo to Right 90° position
def move_servo_right(ser):
    print("Moving servo to Right 90° Position.")
    move_servo(ser, RIGHT_90_POSITION, 1000)
    time.sleep(2)

# Main function
if __name__ == "__main__":
    try:
        ser = serial.Serial('/dev/serial0', baudrate=115200, timeout=1)
        print("Servo movement loop started. Press Ctrl+C to stop.")

        while True:
            move_servo_left(ser)
            move_servo_right(ser)

    except serial.SerialException as e:
        print(f"Error: {e}")

    except KeyboardInterrupt:
        print("\nStopping servo movement.")

    finally:
        ser.close()
