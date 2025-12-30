# qubit-note: RaspeberryPi Series | Connect to RaspberryPi Using Raspberry Pi Connect

## Overview

Raspberry Pi is a very versatile small, low-cost, single-board computer originally designed to help people learn computer science. 
Despite its tiny size (roughly the size of a credit card), it’s fully capable of running an operating system, connecting to the internet, and running software for a wide variety of tasks.
In this qubit-note I will show you how to connect to a Raspberry Pi board using <a href="https://www.raspberrypi.com/documentation/services/connect.html">Raspberry Pi Connect</a>


**keywords** Programming, Raspberry-pi, Embedded-systems

## Connect to RaspberryPi Using Raspberry Pi Connect

There are various ways to connect remotely to your Raspberry Pi and Raspberry Pi Connect is one of them.
Raspberry Pi Connect provides secure access to your Raspberry Pi from anywhere in the world [1].

Connect is installed by default in Raspberry Pi OS Desktop and Raspberry Pi OS Full (desktop with recommended software).
In order to access our board we need to first start Connect and link a device with it:

On your board's terminal type

```
rpi-connect on
```

After starting Connect on your Raspberry Pi device, you must associate your device with your Connect account.
You can do this either via the desktop or the CLI:

```
rpi-connect signin
```

After authenticating, assign a name to your device. Choose a name that uniquely identifies the device.
Visit: https://connect.raspberrypi.com/devices to access your linked devices.

For more information about Raspberry Pi Connect see [1].

## Summary

Raspberry Pi is a small, affordable, single-board computer designed for learning computer science, capable of running an OS, connecting to the internet, and performing various tasks.
This qubit-note explains how to connect to a Raspberry Pi remotely using Raspberry Pi Connect, which provides secure access from anywhere. Raspberry Pi Connect comes pre-installed on Raspberry Pi OS Desktop and Full editions. To use it, you start Connect on the Pi using rpi-connect on, then link the device to your Connect account via rpi-connect signin, assign a unique device name, and manage devices through the Raspberry Pi Connect web portal.

## References

1. <a href="https://www.raspberrypi.com/documentation/services/connect.html">Raspberry Pi Connect</a>