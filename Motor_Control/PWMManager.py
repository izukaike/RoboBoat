import time
from adafruit_pca9685 import PCA9685
import board
#from lib.MotionSmoothing import MotionSmoothing
import MotionSmoothing
from numpy import interp

class PWMManager:
	def __init__(self, frequency = 50):
		self.minDuty = 0
		self.maxDuty = 65535
		self.range = [self.minDuty, self.maxDuty]
		self.i2c = board.I2C()
		self.driver = PCA9685(self.i2c)
		self.setFrequency(frequency)
		self.duty = [None] * 8
		self.calibrated = False
		self.calibrationVal = None

	def calibrate(self, val):
		self.calibrated = True
		self.calibrationVal = val
		self.driver.reference_clock_speed = val
		self.driver.frequency = self.frequency

		
	def setFrequency(self, frequency):
		self.frequency = frequency
		self.periodUs = 1_000_000 / frequency
		self.stepUs = self.periodUs / self.maxDuty
		self.driver.frequency = frequency
		
	def setDuty(self, channel, duty):
		duty = max(self.minDuty,min(duty, self.maxDuty))
		duty = round(duty)
		self.duty[channel] = duty
		self.driver.channels[channel].duty_cycle = duty
	
	def setDutyPercent(self, channel, percent):
		percent = max(0,min(100,percent))
		duty = interp(percent,[0, 100],self.range)
		self.setDuty(channel, duty)
		
	def setDutyNormalized(self, channel, dutyNormalized):
		dutyNormalized = max(0,min(1,dutyNormalized))
		duty = interp(dutyNormalized,[0, 1],self.range)
		PWMManager.setDuty(channel, duty)
	
	def setUs(self, channel, us):
		us = max(0,min(self.periodUs,us))
		duty = us / self.stepUs
		PWMManager.setDuty(channel, duty)
	
	def makeDevice(self, channel, minInput, maxInput, minUs, maxUs):
		return PWMDevice(self, channel, minInput, maxInput, minUs, maxUs)

	def makeServo(self, channel, reverse = False, minInput = 0, maxInput = 180, minUs = 700, maxUs = 2300):
		return PWMDevice(self, channel, 1, reverse, minInput, maxInput, minUs, maxUs)
	
	def makeSmoothServo(self, channel, reverse = False, numSamples = 1, minInput = 0, maxInput = 180, minUs = 700, maxUs = 2300):
		return SmoothedPWMDevice(self, channel, 1, reverse, minInput, maxInput, minUs, maxUs, numSamples)

	def makeBLDCBidir(self, channel, powerLimit = 1, reverse = False, minInput = -100, maxInput = 100, minUs = 900, maxUs = 2100):
		return PWMDevice(self, channel, powerLimit, reverse, minInput, maxInput, minUs, maxUs)

	def makeBLDC(self, channel, powerLimit = 1, reverse = False, minInput = 0, maxInput = 100, minUs = 900, maxUs = 2100):
		return PWMDevice(self, channel, powerLimit, reverse, minInput, maxInput, minUs, maxUs)
	
	def makeSmoothBLDCBidir(self, channel, powerLimit = 1, reverse = False, numSamples = 1, minInput = -100, maxInput = 100, minUs = 900, maxUs = 2100):
		return SmoothedPWMDevice(self, channel, powerLimit, reverse, minInput, maxInput, minUs, maxUs, numSamples)
		

class PWMDevice:
	def __init__(self, manager, channel, powerLimit, reverse, minInput, maxInput, minUs, maxUs):
		self.manager = manager
		self.channel = channel
		self.minInput = minInput
		self.maxInput = maxInput
		self.minUs = minUs
		self.maxUs = maxUs
		self.powerLimit = powerLimit
		self.reverse = reverse
		self.outputRange = [minUs, maxUs]
		self.inputRange = [minInput, maxInput]
		self.position = None
		self.us = None

	def setManager(self, manager):
		self.manager = manager
		
	def setPosition(self, position):
		self.position = max(self.minInput,min(self.maxInput * self.powerLimit, position * self.powerLimit))
		if(self.reverse):
			self.position = interp(self.position, self.inputRange, [self.maxInput, self.minInput])
		self.us = interp(self.position,self.inputRange, self.outputRange)
		self.manager.setUs(self.channel, self.us)

	def cleanPosition(self, position):
		position = max(self.minInput,min(self.maxInput * self.powerLimit, position * self.powerLimit))
		if(self.reverse):
			position = interp(self.position, self.inputRange, [self.maxInput, self.minInput])
		return position

	def pos2Us(self, position):
		return interp(position,self.inputRange, self.outputRange)

	def Us2pos(self, Us):
		return interp(Us,self.outputRange, self.inputRange)
	
	def checkPosition(self, position):
		return abs(self.position - self.cleanPosition(position)) < 0.01

	def setUs(self, us):
		self.us = us
		self.manager.setUs(self.channel, us)

class SmoothedPWMDevice:
	def __init__(self, manager, channel, powerLimit, reverse, minInput, maxInput, minUs, maxUs, smoothingFactor):
		self.pwmDevice = PWMDevice(manager, channel, powerLimit, reverse, minInput, maxInput, minUs, maxUs)
		self.smoother = MotionSmoothing(smoothingFactor)

	def setManager(self, manager):
		self.pwmDevice.setManager(manager)

	def setPosition(self, position):
		position = self.pwmDevice.cleanPosition(position)
		position = self.smoother.addSample(position)
		self.pwmDevice.setPosition(position)

	def checkPosition(self, position):
		return self.pwmDevice.checkPosition(position=position)

	def setUs(self, us):
		position = self.pwmDevice.Us2pos(us)
		position = self.smoother.addSample(position)
		self.pwmDevice.setUs(self.pwmDevice.pos2Us(position))
