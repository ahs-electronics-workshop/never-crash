import adafruit_vl53l4cd
import board

i2c = board.I2C()  # uses board.SCL and board.SDA
vl53 = adafruit_vl53l4cd.VL53L4CD(i2c)

def setup(timing_budget = 50, time_between_measurements = 100):
    vl53.inter_measurement = time_between_measurements # the delay between measurements - larger than timing_budget
    vl53.timing_budget = timing_budget # how long in ms to take a measurement - 10 - 200 ms
    vl53.start_ranging()
    
def read_distance():
    d = None
    try:
        if vl53.data_ready and vl53.range_status in [0]:
            d = vl53.distance
        elif vl53.data_ready and vl53.range_status in [1,2]:
            d = 160
        vl53.clear_interrupt()
    except:
        pass
    return d