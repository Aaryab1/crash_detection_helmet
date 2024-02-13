from imu import MPU6050
from machine import I2C,Pin,reset
from oled import Write, GFX, SSD1306_I2C
from oled.fonts import  ubuntu_20, press_start_2p_20
import math
import time

###########PIN INITILIZATION##################
i2c=I2C(1, sda=Pin(26), scl=Pin(27), freq=400000)
mpu = MPU6050(i2c)


i2c2 = I2C(0,sda=Pin(16),scl =Pin(17), freq= 400000)
dsp=SSD1306_I2C(128,64,i2c2)
write20 = Write(dsp,ubuntu_20)


pin = Pin(28, Pin.IN, Pin.PULL_UP)


uart = machine.UART(0, baudrate=9600, tx=Pin(0), rx=Pin(1))

#################################################
###########VARIABLE DECLARATION##################

rollG=0
pitchG=0
 
rollComp=0
pitchComp=0
 
errorR=0
errorP=0
 
yaw=0
tLoop=0
cnt=0
crash_timer = 0
crash_threshold = 10
crash_status = False






debounce_time=0

while True:
    dsp.fill(0)
    dsp.show()
    i = 10
    while not crash_status:
        tStart=time.ticks_ms()
    
        xGyro=mpu.gyro.x
        yGyro=-mpu.gyro.y
        zGyro=mpu.gyro.z
    
        xAccel=mpu.accel.x
        yAccel=mpu.accel.y
        zAccel=mpu.accel.z
        
        xAccel = max(min(xAccel, 1), -1)
        yAccel = max(min(yAccel, 1), -1)
        zAccel = max(min(zAccel, 1), -1)
        
        rollG=rollG+yGyro*tLoop
        pitchG=pitchG+xGyro*tLoop
        
        rollA=math.atan(xAccel/zAccel)/2/math.pi*360
        pitchA=math.atan(yAccel/zAccel)/2/math.pi*360
        
        rollComp= rollA*.005 + .995*(rollComp+yGyro*tLoop)+errorR*.005
        pitchComp= pitchA*.005 + .995*(pitchComp+xGyro*tLoop)+errorP*.005
        
        errorP=errorP + (pitchA-pitchComp)*tLoop
        errorR=errorR + (rollA-rollComp)*tLoop
        if abs(pitchComp) > 50 or abs(rollComp) > 45:
            crash_timer += tLoop  # Increment crash timer if condition is met
            if crash_timer >= crash_threshold:
                print("Crash Detected")
                crash_status = True
                
                # Add additional actions for crash detection here
                
        else:
            crash_timer = 0
        cnt=cnt+1
        if cnt==10:
            cnt=0
            print('RC: ',rollComp,'PC: ',pitchComp)
            
            #print('RA: ',rollA,'RC: ',rollComp)'''
        tStop=time.ticks_ms()
        tLoop=(tStop-tStart)*.001
    while crash_status and i!= 0:
        dsp.fill(0)
        write20.text("Crash ",0,0)
        write20.text("Detected",0,20)
        write20.text(str(i),0,40)
        i = i - 1
        dsp.show()
        if ((pin.value() is 0) and (time.ticks_ms()-debounce_time) > 300):
            debounce_time=time.ticks_ms()
            print("Button Pressed")
            crash_status = False
            crash_timer = 0
            time.sleep(0.5)
        time.sleep(1)
    
    while crash_status and i == 0:
        dsp.fill(0)
        write20.text("Alert   Sent ",15,20)
        dsp.show()
        uart.write("Hello, world!")

