# RoboBoat
Autonomous Navigation System for Boat

# Full Boat Diagram
<p align="center">
   <img align="middle" alt="Java" width="500px" height="300px"src="https://github.com/user-attachments/assets/742fffdf-3da5-4602-a967-c3886a6e2ee0">
</p>

# Electronics Schematic
<p align="center">
   <img align="middle" alt="Java" width="850px" height="600" height="350px"src="https://github.com/user-attachments/assets/21d40257-a20d-49e6-9029-5e83bc6b3402">
</p>

# Testing Results


<div style="display: flex; align-items: center; justify-content: space-between; gap: 40px; flex-wrap: wrap;">
    <p>The RoboBoat system was tested to make sure it could reliably find and move toward a target on its own, using a simple three-state finite state machine (FSM). The first state, Locate Target, has the boat rotate to scan the area ( rotates CW 90 and CCW 180). Once a target is found, it switches to Approach Target, where it moves forward and adjusts its direction based on image error signal. When it gets close enough, it enters At Target and stops and rotates to stay on target without advancing forward. In testing, the boat consistently oriented itself within 30 degrees of the target, moved more than 20 feet across the water, and completed full rotations as needed to locate targets. Graphs of error signals, thruster behavior, and distance from the target all showed the system responding as expected. There were a few minor glitches in the camera data, but they were rare and didn’t throw off the boat’s behavior. The system used pixel error rather than angle error to simplify the calculations and improve response time, with the hardware PWM module controlling the differential thrust of the left and right motors. Overall, the test results confirmed that the RoboBoat can accurately navigate, react to its environment, and make smooth transitions between states.</p>
  <p align="center">
    <img src="https://github.com/user-attachments/assets/baa7b4d3-000d-45b1-85ac-50ec8dc19493" alt="Testing Result Diagram" width="300px" height="300px">
 </p>
</div>

## &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp;Error Signal&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; L & R Thruster Action &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Distance From Target
<div style="display: flex; justify-content: center; gap: 10px;">
  <div>
    <h3></h3>
    <img src="https://github.com/user-attachments/assets/5c11512f-fde7-477e-9ef7-24ec72924257" alt="Full Boat Diagram" height ="300px" width="333px">
    <img src="https://github.com/user-attachments/assets/d40e7fa0-4230-497b-b922-127d68dbeefa" alt="Electronics Schematic" height ="300px" width="333px">
    <img src="https://github.com/user-attachments/assets/50890a11-6ce5-4d64-ab0b-d71a6e1e8860" alt="Testing Results" height ="300px" width="333px">
  </div>
</div>
