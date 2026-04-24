# simple P
import time
import board
import pwmio
from adafruit_motor import motor
import ew_distance as ew_dist
from adafruit_lsm6ds.lsm6ds3trc import LSM6DS3TRC
import busio
import digtalio

# --- BLUETOOTH CONFIG

import ew_uart as ua
ua.setup("...YOUR NAME...")

# I2C bus and it has its own power pin that we need to enable.
imupwr = digitalio.DigitalInOut(board.IMU_PWR)
imupwr.direction = digitalio.Direction.OUTPUT
imupwr.value = True
time.sleep(0.1)

imu_i2c = busio.I2C(board.IMU_SCL, board.IMU_SDA)
sensor = LSM6DS3TRC(imu_i2c)

# TODO # NOTICE THIS! --- PID  ---
TARGET_DISTANCE = 10.0  # Distance(cm) from object or wall - target use for PID
KP = 0.02        # Proportional in PID - percentage of difference between 
                 # current distance and TARGET_DISTANCE to use for P in PID
KI = 0.0001       # Integral: "How long have I been off-target?"
KD = 0.002        # Derivative: "How fast am I approaching?"

MAX_SPEED = 1.0
MIN_SPEED = 0.3  # the motor won't move unless you are throttling >= 0.3

# TODO Notice this -- NOTHING TO DO
# --- TRACKING VARIABLES ---
last_error = 0
integral = 0
last_time = time.monotonic()

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
    global last_error, integral, last_time
    

    error = KP * error # YOU HAVE THIS FROM LAST TIME
    # 1. Proportional
    P = current_dist - TARGET_DISTANCE # YOU HAVE THIS FROM LAST TIME
    
    
    # 2. Integral (Sum of error over time -- remember this is AREA under the curve)
    integral += ... * ...
    I = ... * ... # LOOK AT KP -- we are taking a tiny piece of the integral to have a sense to allows the cumulative error 
                  # effect our speed
    
    # 3. Derivative (Rate of change of error - what is difference in our error from the last moment)
    # FOR D - Derivative - What does deritive give you? 
    now = time.monotonic()
    dt = now - last_time  # Change in time
    if dt <= 0: 
        dt = 0.001 # Prevent division by zero

    derivative = (... - ...) / ...
    D = ... * ... # Again take a piece of the derivative!  -- see how we did KP
    
    # Save for next loop
    last_error = ...
    last_time = ...
    
    speed =  P + I + D

    # 4:
    # IF speed is larger the MAX_SPEED use MAX_SPEED
    # IF the speed is less than MIN_SPEED use MIN_SPEED 
    return max(MIN_SPEED, min(speed, MAX_SPEED))

def handle_uart(distance, imu_acceleration, imu_gyro):
        counter += 1
        if counter % 50000 == 0:
            if log_distance:
                msg = f"Distance: {distance:.2f};\n"
                ua.write(msg)
            if log_imu:
                msg = f"IMU Acceleration: {imu_acceleration:.2f};\n"
                msg = f"IMU Gyro: {imu_gyro:.2f};\n"
                ua.write(msg)
              
        if ua.in_waiting():
            data = ua.read(ua.in_waiting())
            if data:
                text = data.decode("utf-8").strip()
                print("Text Sent: ", text)
                if text and text == "... WHAT LETTER TO LOG DISTANCE":
                    log_distance = ...
                elif text and text == "... WHAT LETTER TO LOG IMU":
                    log_imu = ...
                elif text and text == "... WHAT LETTER TO STOP LOGGING":
                    log_distance = ...
                    log_imu = ...
            # ... STUDY ew_uart.py - it provided functions for using buttons instead of sending text
             
while True:
    ua.connect()
    while ua.connected():
        # STEP 5: read the distance
        distance = ...
        accel = sensor.acceleration
        gyro = sensor.gyro

        # STEP 9 - do last!
        handle_uart(distance, accel, gyro)
        
        if state == CRUISING and not distance is None:
            # STPE 6: if your distance is within the emergency stop distance - emergency stop!
            if ... < ...: # Emergency threshold
                state = AVOIDING
                ...
            else:
                # STEP 7: PID moment - call the get_pid_throttle
                throttle = ...
                motor1.throttle = ...
                motor2.throttle = ... # Inverted - meaning multiply by -1
                print(throttle, distance) # comment in and out -- eventually your write this to phone see the ua.
                
        elif state == AVOIDING:
            print("Obstacle! Executing 90-degree turn...")
            perform_hard_turn() # Not PID -- turn hard
            state = CRUISING # Reset back to PID cruising
        
        time.sleep(0.05) # 20Hz loop for smooth PID response
