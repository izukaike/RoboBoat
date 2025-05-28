import time
import sys
import math
import board
import busio
import cv2
import numpy as np
from enum import Enum
from PWMManager import PWMManager  # Make sure this exists
from Auto_Control_PWM import Auto_Control_PWM  # Put your class in Auto_Control_PWM.py

import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

################################################################################
# ADS SETUP #
################################################################################
i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c, address=0x40)

# Channel Setup
CHAN_THRUST_L = AnalogIn(ads, ADS.P0) # Left Thruster
CHAN_THRUST_R = AnalogIn(ads, ADS.P1) # Right Thruster
CHAN_BUTTON   = AnalogIn(ads, ADS.P2) # Buttons

################################################################################
# PWM SETUP #
################################################################################
auto = Auto_Control_PWM()

################################################################################
# STATE MACHINE #
################################################################################
class State(Enum):
	LOOK1 = 1
	FOUND_GREEN = 2
	FOUND_RED = 3
	FOUND_BOTH = 4
	LOOK2 = 5

state = State.LOOK1
bool_change_duty = True
bool_autonomous_mode = False

class StateCalibrate(Enum):
	BUTTON = 1
	PUSH_FORWARD = 2
	PULL_BACKWARD = 3
	FINISHED = 4

def CheckAutonomousMode(chan_button, max_button):
	return chan_button.voltage > max_button - 0.2

def PollState(state, chan_button):
	global bool_autonomous_mode
	bool_autonomous_mode = CheckAutonomousMode(chan_button, MAX_BUTTON)
	return bool_autonomous_mode

################################################################################
# CALIBRATION #
################################################################################
state_calibrate = StateCalibrate.BUTTON

while state_calibrate != StateCalibrate.FINISHED:
	if state_calibrate == StateCalibrate.BUTTON:
		BUTTON_PRESS1 = CHAN_BUTTON.voltage
		print("Press the button")
		while abs(CHAN_BUTTON.voltage - BUTTON_PRESS1) < 0.1:
			time.sleep(0.1)
		BUTTON_PRESS2 = CHAN_BUTTON.voltage

		if BUTTON_PRESS2 < BUTTON_PRESS1:
			MIN_BUTTON = BUTTON_PRESS2
			MAX_BUTTON = BUTTON_PRESS1
		else:
			MIN_BUTTON = BUTTON_PRESS1
			MAX_BUTTON = BUTTON_PRESS2

		print(f"Button Calibrated: MAX={MAX_BUTTON:.2f}V MIN={MIN_BUTTON:.2f}V")
		state_calibrate = StateCalibrate.PUSH_FORWARD

	elif state_calibrate == StateCalibrate.PUSH_FORWARD:
		time.sleep(2)
		MAX_VOLTAGE_L = CHAN_THRUST_L.voltage
		MAX_VOLTAGE_R = CHAN_THRUST_R.voltage
		state_calibrate = StateCalibrate.PULL_BACKWARD

	elif state_calibrate == StateCalibrate.PULL_BACKWARD:
		time.sleep(2)
		MIN_VOLTAGE_L = CHAN_THRUST_L.voltage
		MIN_VOLTAGE_R = CHAN_THRUST_R.voltage

		SLOPE_L = 30 / (MAX_VOLTAGE_L - MIN_VOLTAGE_L)
		SLOPE_R = 30 / (MAX_VOLTAGE_R - MIN_VOLTAGE_R)

		Y_INT_L = (MAX_VOLTAGE_L * SLOPE_L) - 65
		Y_INT_R = (MAX_VOLTAGE_R * SLOPE_R) - 65

		print("Slope/Offset L:", SLOPE_L, Y_INT_L)
		print("Slope/Offset R:", SLOPE_R, Y_INT_R)

		state_calibrate = StateCalibrate.FINISHED

################################################################################
# OPENCV SETUP #
################################################################################
red_lower1 = np.array([0, 51, 125], np.uint8)
red_upper1 = np.array([5, 255, 255], np.uint8)
red_lower2 = np.array([175, 51, 125], np.uint8)
red_upper2 = np.array([180, 255, 255], np.uint8)
green_lower = np.array([50, 50, 50], np.uint8)
green_upper = np.array([85, 255, 255], np.uint8)

cap = cv2.VideoCapture(0)
if cap.isOpened():
	width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
	height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
	print("Camera Frame:", width, "x", height)

################################################################################
# MAIN LOOP #
################################################################################
try:
	while True:
		print("Controller Mode")
		while not bool_autonomous_mode:
			# Convert voltages to thrusts
			thrust_l = SLOPE_L * CHAN_THRUST_L.voltage - Y_INT_L
			thrust_r = SLOPE_R * CHAN_THRUST_R.voltage - Y_INT_R

			# Use your class to control PWM
			percent_l = auto.throttle_to_percent(auto.thrust_to_throttle(thrust_l, "forward"))
			percent_r = auto.throttle_to_percent(auto.thrust_to_throttle(thrust_r, "forward"))

			auto.mm.setDutyPercent(auto.left, percent_l)
			auto.mm.setDutyPercent(auto.right, percent_r)

			bool_autonomous_mode = CheckAutonomousMode(CHAN_BUTTON, MAX_BUTTON)
			time.sleep(0.1)

		# AUTONOMOUS MODE
		ret, frame = cap.read()
		hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

		red_mask = cv2.bitwise_or(cv2.inRange(hsv, red_lower1, red_upper1), cv2.inRange(hsv, red_lower2, red_upper2))
		green_mask = cv2.inRange(hsv, green_lower, green_upper)

		red_mask = cv2.dilate(cv2.erode(red_mask, None, iterations=2), None, iterations=2)
		green_mask = cv2.dilate(cv2.erode(green_mask, None, iterations=2), None, iterations=2)

		red_contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
		green_contours, _ = cv2.findContours(green_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

		if red_contours:
			x1, y1, w1, h1 = cv2.boundingRect(max(red_contours, key=cv2.contourArea))
			cv2.rectangle(frame, (x1, y1), (x1+w1, y1+h1), (0, 0, 255), 2)
		if green_contours:
			x2, y2, w2, h2 = cv2.boundingRect(max(green_contours, key=cv2.contourArea))
			cv2.rectangle(frame, (x2, y2), (x2+w2, y2+h2), (0, 255, 0), 2)

		# Draw line between centroids
		if red_contours and green_contours:
			c1x, c1y = round(x1 + w1 / 2), round(y1 + h1 / 2)
			c2x, c2y = round(x2 + w2 / 2), round(y2 + h2 / 2)
			cv2.line(frame, (c1x, c1y), (c2x, c2y), (255, 0, 0), 2)

			error = c1x - width / 2  # Distance from center

			# State logic
			match state:
				case State.LOOK1:
					auto.mm.setDutyPercent(auto.left, 45)
					auto.mm.setDutyPercent(auto.right, 55)
					if green_contours: state = State.FOUND_GREEN
					if red_contours: state = State.FOUND_RED

				case State.FOUND_GREEN:
					auto.mm.setDutyPercent(auto.left, 50)
					auto.mm.setDutyPercent(auto.right, 60)
					if red_contours: state = State.FOUND_BOTH

				case State.FOUND_RED:
					auto.mm.setDutyPercent(auto.left, 60)
					auto.mm.setDutyPercent(auto.right, 50)
					if green_contours: state = State.FOUND_BOTH

				case State.FOUND_BOTH:
					auto.go_to_target(error)
					if not (red_contours or green_contours): state = State.LOOK2

				case State.LOOK2:
					auto.mm.setDutyPercent(auto.left, 55)
					auto.mm.setDutyPercent(auto.right, 65)
					if green_contours: state = State.FOUND_GREEN
					if red_contours: state = State.FOUND_RED

		cv2.imshow("Tracking", frame)
		if cv2.waitKey(1) == ord('q'):
			break

		bool_autonomous_mode = PollState(state, CHAN_BUTTON)

except KeyboardInterrupt:
	cap.release()
	cv2.destroyAllWindows()
	auto.neutral()
	sys.exit()