import time
import pigpio

pi = pigpio.pi()
pi.set_mode(18, pigpio.OUTPUT)

while True:
    pi.write(18, 1)
    time.sleep(0.5)
    pi.write(18, 0)
    time.sleep(0.5)
