import time
import board
import busio
from adafruit_pca9685 import PCA9685

# Set up I2C bus and PCA9685 module
i2c = busio.I2C(board.SCL, board.SDA)  # GPIO 3 (SCL) and GPIO 2 (SDA)
pca = PCA9685(i2c)

# Set PWM frequency to 50Hz for servos
pca.frequency = 50

# Define pulse values for min and max positions (in 16-bit counts)
# 0 = 0% duty, 65535 = 100% duty
def us_to_duty(us):
    return int((us / 20000.0) * 65535)  # 20ms = 50Hz

# Set servo to midpoint (usually around 1500us)
pca.channels[1].duty_cycle = us_to_duty(1500)  # Channel 1
pca.channels[5].duty_cycle = us_to_duty(1500)  # Channel 5

time.sleep(2)

# Sweep example
for pulse in range(700, 2301, 200):  # from 700us to 2300us
    print(f"Setting to {pulse}us")
    pca.channels[1].duty_cycle = us_to_duty(pulse)
    pca.channels[5].duty_cycle = us_to_duty(pulse)
    time.sleep(0.5)

# Turn off signals (optional)
pca.channels[1].duty_cycle = 0
pca.channels[5].duty_cycle = 0
pca.deinit()