# Description

Exchange data from a STM32 board and Lego EV3 using I2C and SMBus with the EV3 as master and the STM32 board as slave. The EV3 brick has ev3dev installed, more info on their documentation: <https://www.ev3dev.org/>

A ready project made for the Nucleo-144 board can be found in `/stm_project` folder, all the added codes for reading and sending data from the stm32 board can be found in file `/stm_project/Core/Src/main.c` of the project. You can find some commented codes for other functions.

A python script for reading motor data, reading and sending data from the ev3 brick can be found in `/ev3`.

Result: <https://youtu.be/Yv2TfS-jht4?si=X5JMjH5inVPc9l42>


[link](ev3-configuration)

# EV3 configuration

## Firmware install

Although the ev3 brick does support I2C for its input ports, it only works out of the box with branded hardwares. For custom connections like with a stm32 board it is necessary to install ev3dev linux-based firmware and run python scripts for those I2C features (in this case I'm using the SMBus protocol which is also compatible with I2C).

You will need an SD card to install the firmware on the ev3 brick. The card should not be bigger than 32GBs as the ev3 brick does not support it. 

First download the zip file for EV3 on the ev3dev website: <https://www.ev3dev.org/downloads/>. Then use a flashing program like [Etcher](https://etcher.balena.io/) to flash the it on the ev3 brick. I had some problems with where the `.zip` file would not be flashed correctly and it kept saying flash failed. This can be fixed by unzipping the file and flashing only the `.img` file.

After flashing turn off the ev3 brick and put the SD card in. It should be running ev3dev firmware now. The home screen now looks like this:

![image](https://github.com/Coconutt69/stm32-ev3/assets/137206541/c5f2b007-7425-4276-aa0a-0e5dd53cf3dd)

To go back to the original firmware just turn off the ev3 and unplug the SD card. 

## Custom wire

To connect witht the stm32 board you will need to make a new wire with one end as the ev3's input port connector, the other end are jumper wires. The ev3's input uses RJ12 ports, but the connector is modified so that it is not compatible with normal RJ12 wires, only LEGO wires:

![image](https://github.com/Coconutt69/stm32-ev3/assets/137206541/e1cf949e-6b04-4e8f-8c43-3a3d854c6e02)

RJ12 (left) vs LEGO Wire (right)

So you can either cut up a LEGO-compatible wire, or use a normal RJ12 connector and just remove the locking mechanism (like I did). The pins for I2C looks like this:

![input](/ev3/input_port.jpg)

We only use the SCL, SDA and GND wire for I2C. 4-4.3V pin can also be used to power the stm board if it does support that. 

This is how my wire looks like:

![image](https://github.com/Coconutt69/stm32-ev3/assets/137206541/3fb3d083-9ccd-4e0f-848f-f9933518acf1)

## Connecting with computer and uploading codes

You can connect the ev3 brick with you computer using SSH and access its termnial. Be sure to connect the ev3 brick with your computer's network first. For detailed tutorial on SSH with ev3dev you can see their page: <https://www.ev3dev.org/docs/tutorials/connecting-to-ev3dev-with-ssh/>

After having access to the ev3's terminal, you can create a new python file with `touch`:

```
touch new_file.py
```

For editing the file you can use `nano`, paste the code from `/ev3/robot.py` of this repository to that new file you just created:

```
nano new_file.py
```

The ev3dev already has all the neccesary python packages, so you can just run the file directly:

```
python3 new_file.py
```

The script runs indefinitely, so everytime you want to stop the python programm use Ctrl+C to cancel it. 

# STM32 configuration

The board used was Nucleo-144 with STM32F429ZIT6 chip. Only one I2C bus is needed to connect to the EV3. Configuration of I2C in CubeMX:

![image](https://github.com/Coconutt69/stm32-ev3/assets/137206541/00c20c7b-3574-4332-aec6-485a278b2591)

Here the stm32's address is set to 0x04, you can change it to whatever you like. Remember to turn off clock stretching (Clock No Stretch Mode - Enabled) because for some reason clock stretching inteferes with the ev3's SMBus protocol and it just does not recognize the stm32's address. 

Connect the SCL, SDA and GND pins of the ev3 to the stm32 and they are now ready to exchange data.

# Code

Full codes are in `/ev3/robot.py` and the while loop of `/stm_project/Core/Src/main.c`

Here are some explaination of the codes.

## On the EV3 brick

Converting to bytes:

```python
speed_left = left_motor.speed.to_bytes(2,'big',signed=True)
speed_right = right_motor.speed.to_bytes(2,'big',signed=True)
tx_speed[:2] = speed_left[:]
tx_speed[2:] = speed_right[:]
```

Data read from motors are stored in `int`. In this case the speed values of the motors never go pass a few thousands, so we only use convert 2 last bytes of the full 4 bytes of `int`. Then those bytes are passed to the tx_speed buffer, two first bytes are for the left motor, two last bytes are for the right motor. For angle values they can go up very high so we will use all 4 bytes. 

We use `write_i2c_block_data` and `read_i2c_block_data` to trasnmit and receive bytes:

```python
bus.write_i2c_block_data(0x04,0,tx_pos)
#bus.write_i2c_block_data(0x04,69,tx_speed)
rx_signal = bus.read_i2c_block_data(0x04,0,2)
```

You can use the commneted function to transmit the speed values. Keep in mind the `write_i2c_block_data(address,offset,data)` method will always transmit one `offset` byte first. So it is actually transmitting the number of bytes in `data` plus one additional byte.

Converting negative numbers:

```python
if signal_left > 127:
  signal_left -= 256
if signal_right > 127:
  signal_right -= 256
```

Because of how negative `int8_t` are stored, the raw byte data will be a wrap-around of the positive number (-1 to 255, -2 to 254, and so on...) so to convert this byte back to the negative `int` in python we need to subtract it by 256.

Here the recieved data is just a number from -100 to 100, so using one byte is enough. However, if you want to transer other kind of data then the bytes need to be patched together and converted to usable data.

The motor can be run using PWM, or with set speed using the ev3's own PID controller. For more ways to control the LEGO motor see <https://ev3dev-lang.readthedocs.io/projects/python-ev3dev/en/stable/motors.html>

## On the STM32 board

As disscussed earlier, the ev3 brick will transmit one additional `offset` byte, so the actual number of bytes needed to read is always one more than needed, in this case 5 bytes for speed and 9 bytes for angle.

![image](https://github.com/Coconutt69/stm32-ev3/assets/137206541/e39c6efe-3a02-447b-848d-c9e8c81b5ba0)

```C
HAL_I2C_Slave_Receive(&hi2c2 ,(uint8_t *)rx_pos, 9,100);
//HAL_I2C_Slave_Receive(&hi2c2 ,(uint8_t *)rx_signal, 5,100);
```

This is just a very simple implementation of using I2C in STM32. You can use other HAL_I2C functions to achieve more using interrputs, I2C registers, etc.

The received bytes need to be patched together to make a `int32_t`:

```C
pos_left = (int32_t) (rx_pos[1]<<24) + (rx_pos[2]<<16) + (rx_pos[3]<<8) + rx_pos[4];
pos_right = (int32_t) (rx_pos[5]<<24) + (rx_pos[6]<<16) + (rx_pos[7]<<8) + rx_pos[8];
```

Each byte corresponds 8 bits of the `int32_t` type, so they need to be shifted to the right place before added together. 

The received signal can then be used for other stuff, like making a custom speed or position regulator.
