from PWMManager import PWMManager, PWMDevice
import time

manager = PWMManager()
testServo = manager.makeDevice(0, 0, 180, 700, 2300)
print("Position 0")
testServo.setPosition(0)
time.sleep(3)
print("Position 180")
testServo.setPosition(180)
time.sleep(3)
print("Position 90")
testServo.setPosition(90)
