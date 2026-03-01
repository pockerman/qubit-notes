# qubit-note: Serial Communication Protocols

## Overview

In this note we will discuss three different serial communication methods. Namely, we will look into

- UART
- I2C
- SPI

## Serial communication protocols

Very often devices have to communicate with each other. So how this can be achieved? There are various ways a device can communicate with another device. Three such protocols are the following

- UART or Universal Asynchronous Receiver/Transmitter
- I2C or Inter-Integrated Circuit
- SPI or Serial Peripheral Interface Bus


### Universal Asynchronous Receiver/Transmitter

Universal Asynchronous Receiver/Transmitter (UART) is a hardware communication module used for asynchronous serial communication between devices. It converts parallel data from a processor into serial form for transmission and converts received serial data back into parallel form. Because it is asynchronous, it does not use a shared clock line; instead, both sides agree on parameters such as baud rate, data bits, parity, and stop bits. A basic UART connection typically uses two lines: TX (transmit) and RX (receive), plus a common ground. UART is widely used in embedded systems, microcontrollers, GPS modules, Bluetooth modules, debugging consoles, and serial ports (e.g., RS-232), offering simple, low-cost, point-to-point communication but without built-in addressing or high-speed capability compared to protocols like SPI or I2C.

On Linux, serial ports usually appear as:

```
/dev/ttyS0        # PC hardware UART
/dev/ttyUSB0      # USB-to-serial adapter
/dev/ttyACM0      # CDC ACM device (e.g., Arduino)
/dev/ttyAMA0      # Raspberry Pi hardware UART

```

We can list these by using

```
ls /dev/tty*
```



### Inter-Integrated circuit

**Inter-Integrated Circuit (I²C)** is a short-distance, low-speed serial communication protocol used to connect integrated circuits on the same board. Developed in 1982 by NXP Semiconductors (originally Philips), it uses just **two wires**: **SDA** (data) and **SCL** (clock). I²C follows a **master-slave architecture**, where one or more masters initiate communication and addressed slave devices respond. Each device has a unique 7-bit or 10-bit address, allowing many devices to share the same bus. It supports standard speeds such as 100 kHz (Standard Mode), 400 kHz (Fast Mode), 1 MHz (Fast Mode Plus), and up to 3.4 MHz (High-Speed Mode). I²C is widely used for connecting sensors, EEPROMs, ADC/DACs, displays, and other peripherals because it minimizes wiring and simplifies board design, though it is not intended for high-speed or long-distance communication.

Here is how we can check if the I2C controller is detected on Linux

```
dmesg | grep -i i2c
```

In order to check if the related modules are load properly

```
lsmod | grep i2c
```

----
**Remark**

You may have to istall ```i2c-tools```

```
sudo apt install i2c-tools

```
----


### Serial peripheral interface bus

SPI  has a higher bandwidth than I2C and is commonly used for connecting to SD cards and other peripherals. 
SPI is different to I2C; I2C uses only two connections, SPI needs at least four and in some cases more.
The connections are:

- SCLK: serial clock
- MOSI: master output, slave input
- MISO (master input, slave output) 
- SS: slave select

Here is how we can check if the SPI controller is detected on Linux

```
dmesg | grep -i spi
```

You should see lines indicating an SPI master/controller was registered.
In order to check if the SPI drivers are loaded we can use


```
lsmod | grep spi

```

----
**Remark**

Very often we may have to enable SPI manuall. On a Rapberry Pi this is done via

```
sudo raspi-config

```

----

Below is a simple Python script that tests SPI

```
import spidev

spi = spidev.SpiDev()
spi.open(0, 0)      # bus 0, device 0
spi.max_speed_hz = 1000000

response = spi.xfer([0x9F])
print(response)

spi.close()

```


## Summary

This note introduces three common serial communication protocols used for device-to-device communication: UART, I2C, and SPI. It explains that UART is an asynchronous, point-to-point protocol using TX and RX lines without a shared clock, commonly appearing on Linux as devices like `/dev/ttyS0` or `/dev/ttyUSB0`. I2C is a two-wire (SDA and SCL), master-slave protocol that supports multiple addressed devices on the same bus and is widely used for sensors and peripherals; on Linux, its presence can be verified using `dmesg` and `lsmod`, often with the help of `i2c-tools`. SPI, which offers higher bandwidth than I2C, uses at least four lines (SCLK, MOSI, MISO, SS) and is commonly used for SD cards and high-speed peripherals; its status can also be checked via `dmesg` and `lsmod`, and it may require manual enabling (e.g., on Raspberry Pi). 


## References

1. <a href="https://en.wikipedia.org/wiki/Universal_asynchronous_receiver-transmitter">Universal asynchronous receiver-transmitter</a>
2. <a href="https://en.wikipedia.org/wiki/Serial_Peripheral_Interface">Serial Peripheral Interface</a>
3. <a href="https://en.wikipedia.org/wiki/I2C">I2C</a>