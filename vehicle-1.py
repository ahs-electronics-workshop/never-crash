# simple P

import time
import board
import pwmio
from adafruit_motor import motor
import ew_distance as ew_dist

# --- PID  ---
TARGET_DISTANCE = 10.0  # Distance(cm) from object or wall - target use for PID
KP = 0.02        # Proportional in PID - percentage of difference between 
                 # current distance and TARGET_DISTANCE to use for P in PID
MAX_SPEED = 1.0
MIN_SPEED = 0.3  # the motor won't move unless you are throttling >= 0.3


# --- STATES ---
CRUISING = "cruising"
AVOIDING = "avoiding"
EMERGENCY_STOP = 5 # THIS SHOULD PROBABLY BE LESS THAN TARGET DISTANCE
state = CRUISING

# DC motor setup
PWM_PIN_A1 = board.D10  # pick any pwm pins on their own channels
PWM_PIN_A2 = board.D9
PWM_PIN_B1 = board.D7  # pick any pwm pins on their own channels
PWM_PIN_B2 = board.D8

pwm_a1 = pwmio.PWMOut(PWM_PIN_A1, frequency=50)
pwm_a2 = pwmio.PWMOut(PWM_PIN_A2, frequency=50)
motor1 = motor.DCMotor(pwm_a1, pwm_a2)

pwm_b1 = pwmio.PWMOut(PWM_PIN_B1, frequency=50)
pwm_b2 = pwmio.PWMOut(PWM_PIN_B2, frequency=50)
motor2 = motor.DCMotor(pwm_b1, pwm_b2)

# start distance reading
ew_dist.setup()

# Functions
def stop_motors():
    # STEP 1: Easy one - set your throttles to zero
    pass

def perform_hard_turn():
    # STEP 8: Back up and then turn ninety degrees
    pass
    
def get_pid_throttle(current_dist):
    # STEP 2: difference between how far you are, current_distance, and the TARGET_DISTANCE 
    error = ...
    
    # STEP 3: USE KP to get a chunk of the error to use for the speed by multiplying by error
    speed = ...

    # STEP 4:
    # IF speed is larger the MAX_SPEED use MAX_SPEED
    # IF the speed is less than MIN_SPEED use MIN_SPEED 
    return max(..., min(..., ...))

while True:
    # STEP 5: read the distance
    distance = ...
    
    if state == CRUISING and not distance is None:
        # STPE 6: if your distance is within the emergency stop distance - emergency stop!
        if ... < ...: # Emergency threshold
            state = AVOIDING
            ...
        else:
            # STEP 7: PID moment - call the get_pid_throttle
            throttle = ...
            motor1.throttle = ...
            motor2.throttle = ... # Inverted
            print(throttle, distance) # comment in and out -- eventually your write this to phone
            
    elif state == AVOIDING:
        print("Obstacle! Executing 90-degree turn...")
        perform_hard_turn() # Not PID -- turn hard
        state = CRUISING # Reset back to PID cruising
        
    time.sleep(0.05) # 20Hz loop for smooth PID response
