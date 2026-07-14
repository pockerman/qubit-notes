# qubit-note: Communnication Protocols

## Overview


Many communication protocols can be separated into two categories: parallel or serial communication. Parallel interfaces transfer several bits at the same time and require a bus to transfer data, whereas serial interfaces transfer data one bit at a time. Serial communication has several rules to follow:

    Data bits: The data you want to send (such as an ASCII character) converted into an 8-bit number.
    Synchronization bits: Start bits and stop bits start the beginning and end to a packet. There is always only one start bit, but there can be up to two stop bits.
    Parity bits: Low-level error checking, which is optional and rarely used due to it slowing down the data transfer.
    Baud rate: How fast data is sent over a serial line - expressed in units of bits/second (bps).

Universal Asynchronous Receiver/Transmitter (UART)

A universal asynchronous receiver/transmitter (UART) is a block that implements serial communication by having both parallel and serial interfaces.

One side (parallel) consists of data lines, and the other side (serial) has the transmit (TX) and receive (RX) lines. Never connect TX to TX and RX to RX! The wires should cross, TX should be connected to RX, and RX should be connected to TX between the separate serial communication devices. UARTs do exist as stand-alone ICs, but they're more commonly found inside microcontrollers.


Serial peripheral interface (SPI)

SPI is an interface bus used to send data between microcontrollers and small components, like sensors and SD cards.

SPI works in a slightly different manner than serial communication - it uses a synchronous data bus rather than an asynchronous data bus. With this in mind, it uses separate lines for data and a clock that keeps both the receiving and transmitting side in perfect sync with one another. The clock is an oscillating signal that tells the receiver exactly when to sample the bits on the data line. This is either the rising or falling edge of the clock signal. When the receiver detects that edge, it will immediately look at the data line to read the next bit. One reason SPI is popular is that the receiving hardware can be a simple shift register - simpler and cheaper than the UART, which is required by asynchronous serial communication.

I2C

The Inter-integrated Circuit (I²C) Protocol is intended to allow multiple "slave" digital integrated circuits ("chips") to communicate with one or more "master" chips.

Like SPI, it is only intended for short distance communications within a single device. Like ASIs (such as RS-232 or UART), it only requires two signal wires to exchange information. SparkFun's Qwiic Connect System takes advantage of the benefits of I²C to allow different sensors, actuators, displays and more to be daisy-chained together with a polarized cable.


## Summary

## Refernces

1. <a href="https://www.sparkfun.com/engineering_essentials?_ga=2.242680834.1480719543.1606562008-353498956.1606562008">Engineering Essentials</a>