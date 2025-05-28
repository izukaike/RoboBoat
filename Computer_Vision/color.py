#STATE MACHINE
#Izukas Setup
#Thruster Setup

import cv2
import numpy as np
import math



black_lower = np.array([0, 0, 0], np.uint8)    # Lower bound for black
black_upper = np.array([179, 50, 50], np.uint8)  # Upper bound for black

orange_lower1 = np.array([5, 150, 100], np.uint8)  # Lower bound for first range
orange_upper1 = np.array([15, 255, 255], np.uint8)  # Upper bound for first range
orange_lower2 = np.array([165, 150, 100], np.uint8)  # Lower bound for second range
orange_upper2 = np.array([179, 255, 255], np.uint8)  # Upper bound for second range


cap = cv2.VideoCapture(0)    # This is the capturing of the Video
if cap.isOpened():
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))            # Setting the frame of camera
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print("Frame size:", width, "x", height)

##### THIS IS WHERE THE TRY WHILE FUNCTION 
#Need to make sure the program is running and set up to start this 
#while bool_autonomous_mode == True:

ret, frame = cap.read()
# Convert frame to HSV color space

##################################### FOR ORANGE ###################################
hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
# Create a mask for the specified color range
orange_mask1 = cv2.inRange(hsv, orange_lower1, orange_upper1)
orange_mask2 = cv2.inRange(hsv, orange_lower2, orange_upper2)
orange_mask = cv2.bitwise_or(orange_mask1, orange_mask2)

#This is to remove noise
orange_mask = cv2.erode(orange_mask, None, iterations=2)
orange_mask = cv2.dilate(orange_mask, None, iterations=2)

#contours to make sure that we are able to reconginze things from each other
orange_contours, _ = cv2.findContours(orange_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)


if orange_contours:
	largest_contour = max(orange_contours, key=cv2.contourArea)
	x1, y1, w1, h1 = cv2.boundingRect(largest_contour)
	cv2.rectangle(frame, (x1, y1), (x1 + w1, y1 + h1), (0, 0, 255), 2)
      
################################## FOR BLACK ####################################
hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

black_mask = cv2.inRange(hsv, black_lower, black_upper)

black_mask = cv2.erode(black_mask, None, iterations=2)
black_mask = cv2.dilate(black_mask, None, iterations=2)

black_contours, _ = cv2.findContours(black_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                                     
if black_contours:
	largest_contour = max(black_contours, key=cv2.contourArea)
	x2, y2, w2, h2 = cv2.boundingRect(largest_contour)
	cv2.rectangle(frame, (x2, y2), (x2 + w2, y2 + h2), (0, 255, 0), 2)

if black_contours:
	c2x = round(x2+1/2*w2)
	c2y = round(y2+1/2*h2)
	center_blackx = c2x
	center_blacky = c2y
	cv2.circle(frame, (round(center_blackx),round(center_blacky)),5,(255,0,255),thickness=3)
	frame_width_center = str(width/2)
	centroid_x = str(center_blackx)
	error = center_blackx - width/2
	if error > 50:                              #change these numbers after testing
		disp2 = "Too far right"
	elif error < -50:
		disp2 = "Too far Left"
	else:
		disp2 = "Perfect"
	err_txt = str(error)
	disp_black = "Error =" + frame_width_center + "-" + centroid_x + "=" + err_txt          #for the control signal
	black_error_final = frame_width_center - centroid_x
	
#How much we drive the motor is going to be proportional to the error that we get

if orange_contours: 
	c1x = round(x1+1/2*w1)
	c1y = round(y1+1/2*h1)
	center_orangex = c1x
	center_orangey = c1y
	cv2.circle(frame, (round(center_orangex),round(center_orangey)),5,(255,0,255),thickness=3)
	frame_width_center = str(width/2)
	centroid_x = str(center_orangex)
	error = center_orangex - width/2
	if error > 50:
		disp2 = "Too far right"
	elif error < -50:
		disp2 = "Too far Left"
	else:
		disp2 = "Perfect"
	err_txt = str(error)
	disp_orange = "Error =" + frame_width_center + "-" + centroid_x + "=" + err_txt
	orange_error_final = frame_width_center - centroid_x
	
#Correct error
#To correct error one will need to take the error text and then move the boat in response to that
#Need to have the distance calculations from the camera as well. 

cv2.putText(frame,disp_orange,(round(width/16),round(height)),cv2.FONT_HERSHEY_PLAIN,1,(0,255,255))
#cv2.putText(frame,disp2,(round(width/16),round(height/8)),cv2.FONT_HERSHEY_PLAIN,1,(0,255,255))
cv2.putText(frame,disp_black,(round(width/16),round(height)),cv2.FONT_HERSHEY_PLAIN,1,(0,255,255))
#cv2.putText(frame,disp2,(round(width/16),round(height/8)),cv2.FONT_HERSHEY_PLAIN,1,(0,255,255))
cv2.imshow("Color Detection and Tracking", frame)	

