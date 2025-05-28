'''

API for PWM Module



'''

from PWMManager import PWMManager, PWMDevice

import time

with open('look1_lt.txt', 'w') as f3:
    pass  
f3.close()
with open('look1_rt.txt', 'w') as f4:
    pass  
f4.close()

f3 = open("look1_lt.txt", "a+")
f4 = open("look1_rt.txt", "a+")

class Auto_Control_PWM():

    def __init__(self):

        self.left = 1

        self.right = 5

        self.mm = PWMManager(500)

        self.PWMCalibration = 23800000

        time.sleep(2)

        self.mm.calibrate(self.PWMCalibration)

        self.mm.setDutyPercent(self.left,0)
        self.mm.setDutyPercent(self.right,0)
    def close(self):
        f3.close()
        f4.close()
    def ramp(self, val):
        for i in range(int(val)):
            '''
            f3.write(str(i))
            f3.write("\n")
            
            f4.write(str(i))
            f4.write("\n")
            '''
            auto.thruster_control(i,"ramp")
            time.sleep(0.005)

    def look(self, dir, speed):
        base = 77.5
        if dir == "CW":
            f3.write(str(base+speed))
            f3.write("\n")
            
            f4.write(str(0))
            f4.write("\n")
            print("f3 = " + str(base+speed))
            print("f4 = " + str(0))
            self.mm.setDutyPercent(self.left,base + speed)
            self.mm.setDutyPercent(self.right,0)
        if dir == "CCW":
            f3.write(str(0))
            f3.write("\n")
            
            f4.write(str(base + speed))
            f4.write("\n")
            
            print("f3 = " + str(0))
            print("f4 = " + str(base+speed))
            self.mm.setDutyPercent(self.left,0)
            self.mm.setDutyPercent(self.right,base + speed)
            
    def test(self, percent):
        self.mm.setDutyPercent(self.right,percent)

        self.mm.setDutyPercent(self.left,percent)
   
    def neutral(self):

        #CHANGE THIS TO 50

        no_motor = 0

        self.mm.setDutyPercent(self.right,no_motor)

        self.mm.setDutyPercent(self.left,no_motor)

    '''simplified'''
    def thruster_control(self,error, action):
        '''HOW TO REVERSE?'''
        #no thruster action until like >75% duty cycle

        #thrust gain
        pixel_width= 320
        base = 77.5
        k = float((100-base)/pixel_width) #change this value
        extra = 200 #change this 
        t = error * k 
        '''turn boat left'''
        if action == "ramp":
            self.mm.setDutyPercent(self.left,base + t)
            #right thruster
            self.mm.setDutyPercent(self.right,base + t)
        elif action == "stay":
            if(error >= 0):
                p_l = base 
                p_r = base + (t/3)
                #left thruster
                f3.write(str(p_l))
                f3.write("\n")
                f4.write(str(p_r))
                f4.write("\n")
                self.mm.setDutyPercent(self.left,p_l)
                #right thruster
                self.mm.setDutyPercent(self.right,p_r)
            elif(error < 0):
                p_l = abs(-base + (t/3))
                p_r = abs(-base )
                f3.write(str(p_l))
                f3.write("\n")
                f4.write(str(p_r))
                f4.write("\n")
                #left thruster
                self.mm.setDutyPercent(self.left,p_l)
                #right thruster
                self.mm.setDutyPercent(self.right,p_r)
        elif action == "go":
            '''Fill in this part'''
            base = 90 # only change
            max_diff = 10
            k = float((100-base)/pixel_width) #change this value
            t = error * k

            if(error >= 0):
                p_l = base + (t/3)
                p_r = base - (t/3)
                #left thruster
                f3.write(str(p_l))
                f3.write("\n")
                f4.write(str(p_r))
                f4.write("\n")
                self.mm.setDutyPercent(self.left,p_l)
                #right thruster
                self.mm.setDutyPercent(self.right,p_r)
            elif(error < 0):
                p_l = abs(-base - (t/3))
                p_r = abs(-base + (t/3))
                #left thruster
                f3.write(str(p_l))
                f3.write("\n")
                f4.write(str(p_r))
                f4.write("\n")
                self.mm.setDutyPercent(self.left,p_l)
                #right thruster
                self.mm.setDutyPercent(self.right,p_r)
            
        
    

auto = Auto_Control_PWM()

'''
ramp_test = False

try: 

#ramp test
    if ramp_test:
        auto.ramp(87.5)
        time.sleep(5)
        auto.neutral()

except KeyboardInterrupt:
    auto.neutral()

auto.neutral()
'''
