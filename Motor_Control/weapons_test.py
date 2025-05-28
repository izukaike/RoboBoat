import RPi.GPIO as GPIO
import time

# Use BCM pin numbering
GPIO.setmode(GPIO.BOARD)

# Set GPIO 16 as output
GPIO.setup(40, GPIO.OUT)

try:
    while True:
        # Set pin 16 HIGH
        GPIO.output(40, GPIO.LOW)
        print("GPIO 16 set to HIGH")
        time.sleep(5)  # wait 5 seconds

        # Set pin 16 LOW
        GPIO.output(40, GPIO.HIGH)
        print("GPIO 16 set to LOW")
        time.sleep(5)  # wait 5 seconds

except KeyboardInterrupt:
    # Graceful exit on Ctrl+C
    print("\nExiting program")

finally:
    # Clean up GPIO settings
    GPIO.cleanup()
