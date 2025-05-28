import cv2
import numpy as np
import time
from pwm_new import Auto_Control_PWM
from enum import Enum

# Color ranges
black_lower = np.array([0, 0, 0], np.uint8)
black_upper = np.array([180, 50, 65], np.uint8)

# Optimized orange ranges (from successful test)
orange_lower1 = np.array([10, 100, 100], np.uint8)
orange_upper1 = np.array([25, 255, 255], np.uint8)
orange_lower2 = np.array([25, 100, 100], np.uint8)  
orange_upper2 = np.array([35, 255, 255], np.uint8)

# Constants
FOCAL_LENGTH = 550
KNOWN_WIDTH_BLACK = 62.0
KNOWN_WIDTH_ORANGE = 60.0


# Initialize camera
#cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
cap = cv2.VideoCapture(0)
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
frame_center = frame_width // 2

def detect_orange(frame):
    """Improved orange detection with glare handling"""
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    orange_mask1 = cv2.inRange(hsv, orange_lower1, orange_upper1)
    orange_mask2 = cv2.inRange(hsv, orange_lower2, orange_upper2)
    orange_mask = cv2.bitwise_or(orange_mask1, orange_mask2)
    
    # Glare reduction
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    _, glare_mask = cv2.threshold(gray, 220, 255, cv2.THRESH_BINARY_INV)
    orange_mask = cv2.bitwise_and(orange_mask, glare_mask)
    
    # Noise removal
    kernel = np.ones((5,5), np.uint8)
    orange_mask = cv2.morphologyEx(orange_mask, cv2.MORPH_OPEN, kernel)
    
    contours, _ = cv2.findContours(orange_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if not contours:
        return None, 0, 0
    
    largest = max(contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(largest)
    center_x = x + w//2
    error = center_x - frame_center
    distance = (KNOWN_WIDTH_ORANGE * FOCAL_LENGTH) / w
    
    return (x, y, w, h), error, distance

def detect_black(frame):
    """Black rectangle detection (only runs if orange not detected)"""
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, black_lower, black_upper)
    
    # Apply morphological operations to clean up the mask
    kernel = np.ones((5,5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    
    # Find contours
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if not contours:
        return None, 0, 0
    
    # Filter contours by area and aspect ratio
    MIN_AREA = 1500
    MIN_ASPECT_RATIO = 3.0
    MAX_ASPECT_RATIO = 6.0
    
    valid_contours = []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < MIN_AREA:
            continue
            
        x, y, w, h = cv2.boundingRect(cnt)
        aspect_ratio = max(w, h) / min(w, h) if min(w, h) > 0 else 0
        
        if MIN_ASPECT_RATIO <= aspect_ratio <= MAX_ASPECT_RATIO:
            valid_contours.append((cnt, area, (x, y, w, h)))
    
    if not valid_contours:
        return None, 0, 0
    
    # Get the largest valid contour
    largest_cnt, _, (x, y, w, h) = max(valid_contours, key=lambda x: x[1])
    
    # Calculate center error and distance
    center_x = x + w//2
    error = center_x - frame_center
    distance = (KNOWN_WIDTH_BLACK * FOCAL_LENGTH) / w
    
    return (x, y, w, h), error, distance




























#clear the file
with open('look1_error.txt', 'w') as f1:
    pass  
f1.close()
with open('look1_state.txt', 'w') as f2:
    pass  
f2.close()
with open('look1_lt.txt', 'w') as f3:
    pass  
f3.close()
with open('look1_rt.txt', 'w') as f4:
    pass  
f4.close()
with open('look1_time.txt', 'w') as f5:
    pass  
f5.close()

with open('app_dist.txt', 'w') as f6:
    pass  
f6.close()

f1 = open("look1_error.txt", "a+")
f2 = open("look1_state.txt", "a+")
f3 = open("look1_lt.txt", "a+")
f4 = open("look1_rt.txt", "a+")
f5 = open("look1_time.txt", "a+")
f6 = open("app_dist.txt", "a+")

#ADD
class state(Enum):
	LOOK1 = 1
	FOUND_BLACK = 2
	FOUND_ORANGE = 3
	APPROACHING_BLACK = 4
	APPROACHING_ORANGE = 5
	FIRE_CANNON = 6
	FIRE_GUN = 7
	default = 8

curr_st = state.LOOK1
next_st = state.LOOK1

auto = Auto_Control_PWM()
auto.ramp(79)
now = time.time()
first = True
try: 
    ti = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Priority detection: Orange first
        orange_rect, orange_err, orange_dist = detect_orange(frame)
        
        if orange_rect:
            # Only process orange if detected
            x, y, w, h = orange_rect
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
            
            if orange_err > 50:
                status = "Too far right (ORANGE)"
            elif orange_err < -50:
                status = "Too far left (ORANGE)"
            else:
                status = "Centered (ORANGE)"
            
            cv2.putText(frame, f"Orange Error: {orange_err}", (x, y-60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,165,255), 2)
            cv2.putText(frame, f"Dist: {orange_dist:.1f}in", (x, y-30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,165,255), 2)
            cv2.putText(frame, status, (x, y-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,165,255), 2)
            
            #if error starts too far from zero it ramps up to that stage
            found = False
            f1.write(str(orange_err))
            f1.write("\n")
            match curr_st:
                #looking for target before engaging target
                case state.LOOK1: 
                    f2.write(str(1))
                    f2.write("\n")
                    print("State = LOOK1")
                    ti = (time.time()-now)
                    f5.write(str(ti))
                    f5.write("\n")
                    if found == False:
                        #on boot up the target is in the front
                        if abs(orange_err) < 20:
                            next_st = state.FOUND_ORANGE
                            found = True
                            auto.neutral()
                            
                        #////////////////////////////////////
                    
                        #go clock wise for 5 seconds and search for target
                        
                        if ti < 10:
                            print("5")
                            print(ti)
                            if abs(orange_err) < 20:
                                next_st = state.FOUND_ORANGE
                                found = True
                                auto.neutral()
                                
                            #continue ramp
                            auto.look("CW",3)
                            time.sleep(0.005)

                        #go clock wise for 10 seconds and search for target
                        #auto.ramp(87.5) # may not be needed
                        
                        if ti >  10 and ti < 10.5:
                            auto.ramp(77.5+3)
                                                    
                        if ti  <  30 and ti > 10 and found == False:
                            print("10")
                            print(ti)
                            if abs(orange_err) < 20:
                                next_st = state.FOUND_ORANGE
                                found = True
                                auto.neutral()
                            auto.look("CCW",3)
                            time.sleep(0.005)
                        
                        if ti > 10:
                            auto.neutral()

                    curr_st = next_st
                    print(str(found))
                case state.FOUND_ORANGE:
                    f2.write(str(2))
                    f2.write("\n")
                    '''
                    f3.write(str(0))
                    f3.write("\n")
                    f4.write(str(0))
                    f4.write("\n")
                    '''
                    ti = (time.time()-now)
                    f5.write(str(ti))
                    f5.write("\n")
                    
                    f6.write(str(orange_dist))
                    f6.write("\n")
                    if orange_dist < 24:
                        next_st = state.APPROACHING_ORANGE
                    
                    print("State = FOUND_ORANGE")
                    print(str(found))
                    if first == True:
                        auto.ramp(90)
                        first = False
                    
                    found = False
                    auto.thruster_control(orange_err,"go")
                    if orange_dist <  60:
                        next_st = state.APPROACHING_ORANGE
                    curr_st = next_st
                case state.APPROACHING_ORANGE:
                    f2.write(str(3))
                    f2.write("\n")
                    ti = (time.time()-now)
                    f5.write(str(ti))
                    f5.write("\n")
                    f6.write(str(orange_dist))
                    f6.write("\n")
                    # i made need a ramp
                    print("State = APPROACHING_ORANGE")
                    #auto.neutral()
                    auto.thruster_control(orange_err, "stay")
                    # it will stay here



            
            print("loop")
                
            
            # Explicitly mark black as ignored
            cv2.putText(frame, "BLACK IGNORED (ORANGE DETECTED)", 
                       (50, frame_height-30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,255), 2)
            
        else:
            # Only detect black if orange not found
            black_rect, black_err, black_dist = detect_black(frame)
            
            if black_rect:

                x, y, w, h = black_rect
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                
                if black_err > 50:
                    status = "Too far right (BLACK)"
                elif black_err < -50:
                    status = "Too far left (BLACK)"
                else:
                    status = "Centered (BLACK)"
                
                cv2.putText(frame, f"Black Error: {black_err}", (x, y-60), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)
                cv2.putText(frame, f"Dist: {black_dist/12:.1f}ft", (x, y-30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)
                cv2.putText(frame, status, (x, y-10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)

        
        cv2.imshow('Detection (Orange Priority)', frame)
        if cv2.waitKey(1) == ord('q'):
            break
        start = True
        time.sleep(0.2)

    cap.release()
    cv2.destroyAllWindows()
except KeyboardInterrupt:
    auto.neutral()
    auto.close()
    f1.close()
    f2.close()
    f3.close()
    f4.close()
    f5.close()
    f6.close()
