import sys
from time import sleep
from smbus import SMBus

from ev3dev2.port import LegoPort
from ev3dev2.motor import LargeMotor, OUTPUT_A, OUTPUT_D
from ev3dev2.sensor import INPUT_1
from ev3dev2.motor import Motor

# Set LEGO port for input port 1
in1 = LegoPort(INPUT_1)
in1.mode = 'other-i2c'
# Short wait for the port to get ready
sleep(0.5)

bus = SMBus(3) # Input port 1 on the EV3
tx_speed = [0,0,0,0] # speed buffer, using 2 bytes for each wheel
tx_pos = [0,0,0,0,0,0,0,0] # angle buffer, using 4 bytes for each wheel

# Set LEGO out put ports D and A for the motors
left_motor = LargeMotor(OUTPUT_D)
right_motor = LargeMotor(OUTPUT_A)

print("started")
while(1):
        try:
                # read motor speeds and convert them to bytes
                speed_left = left_motor.speed.to_bytes(2,'big',signed=True)
                speed_right = right_motor.speed.to_bytes(2,'big',signed=True)
                tx_speed[:2] = speed_left[:]
                tx_speed[2:] = speed_right[:]

                # read motor angles and convert them to bytes
                pos_left = left_motor.position.to_bytes(4,'big',signed=True)
                pos_right = right_motor.position.to_bytes(4,'big',signed=True)
                tx_pos[:4] = pos_left[:]
                tx_pos[4:] = pos_right[:]

                # I2C read/write functions
                bus.write_i2c_block_data(0x04,0,tx_pos)
                #bus.write_i2c_block_data(0x04,69,tx_speed)
                rx_signal = bus.read_i2c_block_data(0x04,0,2)

                # convert negative numbers
                signal_left = rx_signal[0]
                signal_right = rx_signal[1]
                if signal_left > 127:
                        signal_left -= 256
                if signal_right > 127:
                        signal_right -= 256

                # set motor PWM duty cycle
                left_motor.duty_cycle_sp = signal_left
                right_motor.duty_cycle_sp = signal_right

                # run motor with PWM
                left_motor.run_direct()
                right_motor.run_direct()

                # use this for setting motor speed with EV3's own PID
                #left_motor.on(signal_left)
                #right_motor.on(signal_right)

                #print(signal_left, signal_right)

        except OSError:
                print("lost connection")

        except:
                left_motor.reset()
                right_motor.reset()
                raise
