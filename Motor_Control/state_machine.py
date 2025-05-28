#State Machine

from enum import Enum

class State(Enum):
	LOOK1 = 1
	FOUND_BLACK = 2
	FOUND_ORANGE = 3
	CLOSE_TO_BLACK = 4
	CLOSE_TO_ORANGE = 5
	default = 6

""""
#Go into the look state first
state = State.LOOK1
bool_change_duty = True



bool_autonomous_mode = True

"""
"""
#This will be going into autonomous mode
def CheckAutonomousMode(CHAN_BUTTON, MAX_BUTTON):
	if CHAN_BUTTON.voltage > MAX_BUTTON - 0.2:
		bool_autonomous_mode = True
	else:
		bool_autonomous_mode = False
	return bool_autonomous_mode

# Polling
def PollState(state, CHAN_BUTTON):
	print(state)
	sleep(.1)
	bool_autonomous_mode = CheckAutonomousMode(CHAN_BUTTON, MAX_BUTTON)
	
	return bool_autonomous_mode
"""

	sleep(.1)
	bool_autonomous_mode = CheckAutonomousMode(CHAN_BUTTON, MAX_BUTTON)
	
	return bool_autonomous_mode
