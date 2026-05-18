import time
import board
import busio
from adafruit_lsm6ds.lsm6ds3 import LSM6DS3
from imu_calibration as imuc

#we may need to call the calibration
#imuc.main()

i2c = busio.I2C(board.IMU_SCL, board.IMU_SDA)
imu = LSM6DS3(i2c)

# Dead-band threshold (°/s) — ignore gyro noise below this
DEAD_BAND = 1.5

# Turn detection threshold (°/s)
TURN_THRESHOLD = 30.0

yaw_angle = 0.0
last_time = time.monotonic()
turning = False


while True:
    now = time.monotonic()
    dt = now - last_time
    last_time = now

    gyro_z = imu.gyro[2] * (180 / 3.14159)   ## WHY THIS MOMENT

    if abs(gyro_z) > DEAD_BAND:
        # Turn just started
        if not turning:
            yaw_angle = 0.0       # reset at the start of each turn
            turning = True

        yaw_angle += gyro_z * dt

        if gyro_z > TURN_THRESHOLD:
            print(f"TURNING RIGHT  |  {yaw_angle:.1f}°")
        elif gyro_z < -TURN_THRESHOLD:
            print(f"TURNING LEFT   |  {yaw_angle:.1f}°")

    else:
        # Vehicle is straight / stopped
        if turning:
            print(f"Turn complete: {yaw_angle:.1f}°")  # final angle of that turn
        turning = False
