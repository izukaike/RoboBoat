'''
API for PWM Module

 - features

4/2/25

4/14/25
 - does not turn on until ~70 percent PWM
'''

from PWMManager import PWMManager, PWMDevice
import time

class Auto_Control_PWM():
    def __init__(self):
        self.left = 1;
        self.right = 5;
        self.mm = PWMManager(500)
        self.PWMCalibration = 23800000
        time.sleep(2)
        self.mm.calibrate(self.PWMCalibration)
    
    def test(self, percent):
        no_motor = 77.5
        self.mm.setDutyPercent(self.right,percent)
        self.mm.setDutyPercent(self.left,percent)
    def neutral(self):
        #CHANGE THIS TO 50
        no_motor = 77.5
        self.mm.setDutyPercent(self.right,no_motor)
        self.mm.setDutyPercent(self.left,no_motor)
    def thrust_to_throttle(self,thrust, direction):
        maxi = 1.7
        mini = 1.3
        zero = 1.5
        max_t = 30
        if thrust > 30:
            return 1.7
        elif thrust < 0:
            return 1.5

        if direction == "forward":
            slope = (maxi-zero) / max_t  # Forward: from 0 to 30 kg
            return 1.5 + slope * thrust
        elif direction == "reverse":
            slope = (zero-mini) / max_t  # Reverse: from 0 to -30 kg
            return zero + slope * thrust  # still adds because thrust is negative
            
    def throttle_to_percent(self,throttle):
        return throttle*50
    
    
        
        
    
    def locate_target(self):
        #rotate 90 degrees counter-clockwise in 5 seconds
        # 7 percent differential (50 is neutral)
        r = 5 # kg
        l = 4.88 # kg
        r_throt = self.thrust_to_throttle(r, "forward")
        l_throt = self.thrust_to_throttle(l, "reverse")
        
        rp = self.throttle_to_percent(r_throt)
        lp = self.throttle_to_percent(l_throt)
        self.mm.setDutyPercent(self.right,rp)
        self.mm.setDutyPercent(self.left,lp)
        
        time.sleep(7)
        
        #rotoate 180 degress clockwise in 10 seconds
        self.mm.setDutyPercent(self.right,lp)
        self.mm.setDutyPercent(self.left,rp)
        
        time.sleep(14)
        
    
    def go_to_target(self, error):
        #all adjustable
        base_thrust = 5.0               # Forward thrust in kg (both motors)
        max_steer_thrust = 5.0       # Max difference between left and right (kg)
        max_thrust = 30.0               # Safety cap for max thrust
        steering_gain = 0.02
        
        #steering offset
        steering_thrust = error * steering_gain
        steering_thrust = max(-max_steer_thrust, min(max_steer_thrust, steering_thrust))
        
        # Left gets more thrust if target is right (positive error), and vice versa
        left_thrust  = base_thrust + steering_thrust
        right_thrust = base_thrust - steering_thrust
        
        left_thrust = max(0, min(max_thrust, left_thrust))
        right_thrust = max(0, min(max_thrust, right_thrust))
        
        left_throttle = self.thrust_to_throttle(left_thrust, "forward")
        right_throttle = self.thrust_to_throttle(right_thrust, "forward")

        left_percent = self.throttle_to_percent(left_throttle)
        right_percent = self.throttle_to_percent(right_throttle)

        self.mm.setDutyPercent(self.left, left_percent)
        self.mm.setDutyPercent(self.right, right_percent)
        
    def stay_in_place(self,error):
        base_thrust = 3.0
        max_error = 100
        differential_gain = 0.01
        min_thrust = 0.5
        error_deadzone = 5

        if abs(error) < error_deadzone:
            self.neutral()
            return

        error = max(-max_error, min(max_error, error))
        differential = differential_gain * error
        differential = max(-1, min(1, differential))

        if differential > 0:
            # Turn right
            left_thrust = base_thrust * (1 - differential)
            right_thrust = base_thrust * (1 + differential)

            left_throttle = self.thrust_to_throttle(left_thrust, "reverse")
            right_throttle = self.thrust_to_throttle(right_thrust, "forward")
        else:
            # Turn left
            left_thrust = base_thrust * (1 + abs(differential))
            right_thrust = base_thrust * (1 - abs(differential))

            left_throttle = self.thrust_to_throttle(left_thrust, "forward")
            right_throttle = self.thrust_to_throttle(right_thrust, "reverse")

        left_throttle = max(left_throttle, self.thrust_to_throttle(min_thrust, "forward"))
        right_throttle = max(right_throttle, self.thrust_to_throttle(min_thrust, "forward"))

        left_percent = self.throttle_to_percent(left_throttle)
        right_percent = self.throttle_to_percent(right_throttle)

        self.mm.setDutyPercent(self.left, left_percent)
        self.mm.setDutyPercent(self.right, right_percent)

        
        
        

    
auto = Auto_Control_PWM()
try:
   i = 0
   auto.locate_target()
   '''
   while True:
        auto.test(i % 100)
        print(i)
        time.sleep(0.1)
        i = i + 1
    '''
except KeyboardInterrupt:
    auto.neutral()



