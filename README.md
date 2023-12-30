# Description

Exchange data from a STM32 board and Lego EV3 using I2C and SMBus with the EV3 as master and the STM32 board as slave. The EV3 block has ev3dev installed, more info on their documentation: <https://www.ev3dev.org/>

A ready project made for the Nucleo-144 board can be found in `/stm_project` folder, all the added codes for reading and sending data from the stm32 board can be found in file `/stm_project/Core/Src/main.c` of the project. 

A python script for reading motor data, reading and sending data from the ev3 block can be found in `/ev3`.

Result: <https://youtu.be/Yv2TfS-jht4?si=X5JMjH5inVPc9l42>

# EV3 configuration

## Firmware install

Although the ev3 block does support I2C for its input ports, it only works out of the box with branded hardwares. For custom connections like with a stm32 board it is necessary to install ev3dev linux-based firmware and run python scripts for those I2C features (in this case I'm using the SMBus protocol which is also compatible with I2C).

You will need an SD card to install the firmware on the ev3 block. The card should not be bigger than 32GBs as the ev3 block does not support it. 

First download the zip file for EV3 on the ev3dev website: <https://www.ev3dev.org/downloads/>. Then use a flashing program like [Etcher](https://etcher.balena.io/) to flash the it on the ev3 block. I had some problems with where the `.zip` file would not be flashed correctly and it kept saying flash failed. This can be fixed by unzipping the file and flashing only the `.img` file.

After flashing turn off the ev3 block and put the SD card in. It should be running ev3dev firmware now. The home screen now looks like this:

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

You can connect the ev3 block with you computer using SSH and access its termnial. Be sure to connect the ev3 block with your computer's network first. For detailed tutorial on SSH with ev3dev you can see their page: <https://www.ev3dev.org/docs/tutorials/connecting-to-ev3dev-with-ssh/>

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

Full codes are in `/ev3/robot.py` and `stm_project/Core/Src/main.c`

## On the EV3 brick
