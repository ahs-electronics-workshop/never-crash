# SPDX-FileCopyrightText: 2024 Your Name
# SPDX-License-Identifier: MIT
"""
IMU Calibration for XIAO nRF52840 Sense
- Gyro bias calibration (stationary)
- 6-point accelerometer calibration
- Saves calibration to file
"""

import time
import board
import busio
import storage
from adafruit_lsm6ds.lsm6dsox import LSM6DSOX  

class IMUCalibration:
    def __init__(self):
        """Initialize I2C and sensor"""
        print("Initializing IMU...")
        i2c = busio.I2C(board.SCL, board.SDA)
        self.sensor = LSM6DSOX(i2c)
        
        # Calibration storage
        self.gyro_offset = [0.0, 0.0, 0.0]
        self.accel_offset = [0.0, 0.0, 0.0]
        self.accel_scale = [1.0, 1.0, 1.0]
        
        self.calibrated = False
        print("IMU ready!")
    
    def calibrate_gyro_bias(self, samples=500):
        """Gyro calibration - sensor must be STILL"""
        print("\n" + "="*40)
        print("GYRO CALIBRATING - Keep sensor COMPLETELY STILL!")
        print("="*40)
        
        # Countdown
        for i in range(3, 0, -1):
            print(f"{i}...")
            time.sleep(1)
        
        print("Collecting data...")
        
        # Collect samples
        sum_x = sum_y = sum_z = 0.0
        
        for i in range(samples):
            gx, gy, gz = self.sensor.gyro
            sum_x += gx
            sum_y += gy
            sum_z += gz
            
            # Progress indicator
            if i % 100 == 0:
                print(f"Samples: {i}/{samples}")
            time.sleep(0.01)  # 10ms between samples
        
        # Calculate offsets (average)
        self.gyro_offset[0] = sum_x / samples
        self.gyro_offset[1] = sum_y / samples
        self.gyro_offset[2] = sum_z / samples
        
        print("\n Gyro Calibration Complete!")
        print(f"Offsets (rad/s):")
        print(f"  X: {self.gyro_offset[0]:.6f}")
        print(f"  Y: {self.gyro_offset[1]:.6f}")
        print(f"  Z: {self.gyro_offset[2]:.6f}")
        
        return self.gyro_offset
    
    def calibrate_accel_6point(self, samples=100):
        """6-position accelerometer calibration"""
        print("\n" + "="*40)
        print("ACCELEROMETER 6-POINT CALIBRATION")
        print("="*40)
        print("Orient the sensor in 6 different positions")
        print("Press Enter after placing in each position...")
        
        positions = [
            "1/6: Z-axis UP (flat, facing up)",
            "2/6: Z-axis DOWN (flat, facing down)",
            "3/6: X-axis UP (X pointing to sky)",
            "4/6: X-axis DOWN (X pointing to ground)",
            "5/6: Y-axis UP (Y pointing to sky)",
            "6/6: Y-axis DOWN (Y pointing to ground)"
        ]
        
        measurements = []
        
        for pos_num, pos_desc in enumerate(positions):
            print(f"\n{pos_desc}")
            input("Press Enter when ready...")
            
            # Small delay to stabilize
            time.sleep(1)
            
            # Collect samples
            sum_x = sum_y = sum_z = 0.0
            for i in range(samples):
                ax, ay, az = self.sensor.acceleration
                sum_x += ax
                sum_y += ay
                sum_z += az
                time.sleep(0.01)
            
            # Store average
            measurements.append((
                sum_x / samples,
                sum_y / samples,
                sum_z / samples
            ))
            
            print(f"Recorded: X={measurements[-1][0]:.3f}, "
                  f"Y={measurements[-1][1]:.3f}, "
                  f"Z={measurements[-1][2]:.3f} m/s²")
        
        # Calculate scale and offset for each axis
        # Z axis (positions 0 and 1)
        z_scale = (2 * 9.80665) / (measurements[0][2] - measurements[1][2])
        z_offset = (measurements[0][2] + measurements[1][2]) / 2
        
        # X axis (positions 2 and 3)
        x_scale = (2 * 9.80665) / (measurements[2][0] - measurements[3][0])
        x_offset = (measurements[2][0] + measurements[3][0]) / 2
        
        # Y axis (positions 4 and 5)
        y_scale = (2 * 9.80665) / (measurements[4][1] - measurements[5][1])
        y_offset = (measurements[4][1] + measurements[5][1]) / 2
        
        self.accel_scale = [x_scale, y_scale, z_scale]
        self.accel_offset = [x_offset, y_offset, z_offset]
        
        print("\n Accelerometer Calibration Complete")
        print(f"X: scale={x_scale:.6f}, offset={x_offset:.6f}")
        print(f"Y: scale={y_scale:.6f}, offset={y_offset:.6f}")
        print(f"Z: scale={z_scale:.6f}, offset={z_offset:.6f}")
        
        return self.accel_offset, self.accel_scale
    
    def verify_calibration(self, samples=50):
        """Verify calibration by checking stationary readings"""
        print("\n" + "="*40)
        print("VERIFYING CALIBRATION")
        print("Place sensor flat (Z up) and still")
        print("="*40)
        
        time.sleep(3)
        
        # Collect calibrated readings
        sum_g = [0.0, 0.0, 0.0]
        sum_a = [0.0, 0.0, 0.0]
        
        for i in range(samples):
            # Gyro (calibrated)
            gx, gy, gz = self.get_calibrated_gyro()
            sum_g[0] += gx
            sum_g[1] += gy
            sum_g[2] += gz
            
            # Accel (calibrated)
            ax, ay, az = self.get_calibrated_accel()
            sum_a[0] += ax
            sum_a[1] += ay
            sum_a[2] += az
            
            if i % 10 == 0:
                print(".", end="")
            time.sleep(0.01)
        
        print("\n\nResults (averages):")
        print(f"Gyro (should be near 0 rad/s):")
        print(f"  X: {sum_g[0]/samples:.6f}")
        print(f"  Y: {sum_g[1]/samples:.6f}")
        print(f"  Z: {sum_g[2]/samples:.6f}")
        
        print(f"\nAccel (should be 0,0,9.81 m/s²):")
        print(f"  X: {sum_a[0]/samples:.3f}")
        print(f"  Y: {sum_a[1]/samples:.3f}")
        print(f"  Z: {sum_a[2]/samples:.3f}")
        
        # Check magnitude
        mag = ((sum_a[0]/samples)**2 + 
               (sum_a[1]/samples)**2 + 
               (sum_a[2]/samples)**2)**0.5
        print(f"\nMagnitude: {mag:.3f} m/s² (should be 9.81)")
        
        # Quality assessment
        print("\nQuality Check:")
        if abs(mag - 9.80665) < 0.1:
            print("Excellent calibration!")
        elif abs(mag - 9.80665) < 0.2:
            print("Good calibration")
        else:
            print("Poor calibration - consider recalibrating")
    
    def get_calibrated_gyro(self):
        """Return gyro with bias removed"""
        raw = self.sensor.gyro
        return (raw[0] - self.gyro_offset[0],
                raw[1] - self.gyro_offset[1],
                raw[2] - self.gyro_offset[2])
    
    def get_calibrated_accel(self):
        """Return accel with offset and scale applied"""
        raw = self.sensor.acceleration
        return ((raw[0] - self.accel_offset[0]) * self.accel_scale[0],
                (raw[1] - self.accel_offset[1]) * self.accel_scale[1],
                (raw[2] - self.accel_offset[2]) * self.accel_scale[2])
    
    def save_calibration(self, filename="/calibration.txt"):
        """Save calibration to file"""
        print(f"\nSaving calibration to {filename}...")
        try:
            with open(filename, "w") as f:
                f.write("# IMU Calibration Data\n")
                f.write(f"# Generated: {time.localtime()}\n\n")
                
                f.write("# Gyro offsets (rad/s)\n")
                f.write(f"GYRO_OFFSET,{self.gyro_offset[0]:.8f},"
                       f"{self.gyro_offset[1]:.8f},{self.gyro_offset[2]:.8f}\n\n")
                
                f.write("# Accelerometer offsets (m/s²)\n")
                f.write(f"ACCEL_OFFSET,{self.accel_offset[0]:.8f},"
                       f"{self.accel_offset[1]:.8f},{self.accel_offset[2]:.8f}\n\n")
                
                f.write("# Accelerometer scale factors\n")
                f.write(f"ACCEL_SCALE,{self.accel_scale[0]:.8f},"
                       f"{self.accel_scale[1]:.8f},{self.accel_scale[2]:.8f}\n")
            
            print("Calibration saved successfully!")
            return True
        except Exception as e:
            print(f"Error saving calibration!: {e}")
            return False
    
    def load_calibration(self, filename="/calibration.txt"):
        """Load calibration from file"""
        print(f"Loading calibration from {filename}...")
        try:
            with open(filename, "r") as f:
                for line in f:
                    if line.startswith("#") or not line.strip():
                        continue
                    
                    parts = line.strip().split(',')
                    if parts[0] == "GYRO_OFFSET":
                        self.gyro_offset = [float(parts[1]), float(parts[2]), float(parts[3])]
                    elif parts[0] == "ACCEL_OFFSET":
                        self.accel_offset = [float(parts[1]), float(parts[2]), float(parts[3])]
                    elif parts[0] == "ACCEL_SCALE":
                        self.accel_scale = [float(parts[1]), float(parts[2]), float(parts[3])]
            
            self.calibrated = True
            print("Calibration loaded successfully!")
            
            # Show loaded values
            print("\nLoaded values:")
            print(f"Gyro offsets: {self.gyro_offset}")
            print(f"Accel offsets: {self.accel_offset}")
            print(f"Accel scales: {self.accel_scale}")
            
            return True
        except Exception as e:
            print(f"No calibration file found: {e}")
            return False

def main():
    """Main calibration routine"""
    print("\n" + "="*60)
    print("XIAO nRF52840 Sense - Tier 2 IMU Calibration")
    print("="*60)
    
    cal = IMUCalibration()
    
    # Try to load existing calibration
    if cal.load_calibration():
        print("\nCalibration found. Verify or recalibrate?")
        print("Press:")
        print("  V - Verify existing calibration")
        print("  R - Recalibrate")
        print("  Any other key - Skip")
        
        choice = input().strip().upper()
        if choice == 'V':
            cal.verify_calibration()
            return
        elif choice == 'R':
            print("\nProceeding with recalibration...")
        else:
            print("Using existing calibration.")
            return
    
    # Run full calibration
    print("\nStarting full calibration...")
    
    # Gyro calibration
    cal.calibrate_gyro_bias(samples=500)
    
    # Accelerometer calibration
    cal.calibrate_accel_6point(samples=100)
    
    # Verify
    cal.verify_calibration()
    
    # Save
    # cal.save_calibration()
    
    print("\n Calibration Complete!")
    print("You can now use these values in your main program.")
    print("\nTo use in your code, copy these lines:")
    print("\n# Calibration values")
    print(f"GYRO_OFFSET = {cal.gyro_offset}")
    print(f"ACCEL_OFFSET = {cal.accel_offset}")
    print(f"ACCEL_SCALE = {cal.accel_scale}")
