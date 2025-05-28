import cv2
import numpy as np
import time

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
cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
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
    
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if not contours:
        return None, 0, 0
    
    largest = max(contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(largest)
    center_x = x + w//2
    error = center_x - frame_center
    distance = (KNOWN_WIDTH_BLACK * FOCAL_LENGTH) / w
    
    return (x, y, w, h), error, distance

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    # Priority detection: Orange first
    #orange_rect, orange_err, orange_dist = detect_orange(frame)
    
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
    
    #cv2.imshow('Detection (Orange Priority)', frame)
    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
