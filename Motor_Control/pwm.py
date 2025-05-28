'''

API for PWM Module



'''



from PWMManager import PWMManager, PWMDevice

import time



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
    def look( dir, speed):
      base = 70
      if dir == "CW":
          self.mm.setDutyCycle(self.left,base + speed)
          self.mm.setDutyCycle(self.right,0)
      if dir == "CCW":
          self.mm.setDutyCycle(self.left,0)
          self.mm.setDutyCycle(self.right,base + speed)
              

    def test(self, percent):
        self.mm.setDutyPercent(self.right,percent)

        self.mm.setDutyPercent(self.left,percent)

        
    def neutral(self,i):

        #CHANGE THIS TO 50

        no_motor = 0

        self.mm.setDutyPercent(self.right,i)

        self.mm.setDutyPercent(self.left,i)

    def thruster_control(self,error, action):
        '''HOW TO REVERSE?'''
        #no thruster action until like >75% duty cycle

        #thrust gain
        pixel_width= 320
        base = 77.5
        k = float((100-base)/pixel_width) #change this value
        t = error * k 
        '''turn boat left'''
        if(error >= 0):
            p_l =  base + t
            print(p_l)
            p_r =  base  + (t/3)
            
            #print("p_l = " + str(p_l) + ", p_l = " + str(p_r))
            #left thruster
            print("1")
            div_l = float(t/10)
            div_r = float(t/30)
            self.mm.setDutyPercent(self.left,p_l)
                #right thruster
            self.mm.setDutyPercent(self.right,p_r)
            '''
            for i in range (10):
                self.mm.setDutyPercent(self.left,base + div_l *i)
                #right thruster
                self.mm.setDutyPercent(self.right,base + div_r*i)
                time.sleep(0.001)
            '''
        elif(error < 0):
            print("2")
            p_l = abs(-base + (t/3))
            p_r = abs(-base + t)
            #left thruster
            self.mm.setDutyPercent(self.left,p_l)
            #right thruster
            self.mm.setDutyPercent(self.right,p_r)
        '''
        elif( error < 20 and error > -20 ):
            print("3")
            #if away from target then you want to move forwarf
            if(action == "go"):
                self.go()
            elif(action == "stay"): 
                mini = 0
                #left thruster
                self.mm.setDutyPercent(self.left,mini)
                #right thruster
                self.mm.setDutyPercent(self.right,mini)
        '''
    def go(self):
         for i in range(50):
             self.mm.setDutyPercent(self.left,i)
             self.mm.setDutyPercent(self.right,i)
             time.sleep(0.1)

'''
auto = Auto_Control_PWM()
time.sleep(5)
try:
    for i in range(320):
        auto.thruster_control(i,"go")
        time.sleep(0.2)
    auto.neutral(0)
except KeyboardInterrupt:

    auto.neutral(0)
'''



