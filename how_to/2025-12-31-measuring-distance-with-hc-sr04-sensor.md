# qubit-note: RaspeberryPi Series | Measuring Distance With HC-SR04 Sensor


## Overview

In  this qubit-note will show how to measure distance using the popular  HC-SR04 ultrasonic distance
sensor. In addition, we will be sendin the measured distance to be consumed by a process running on a different machine via MQTT.
We will be working with Raspberry Pi 5 in this note.

**keywords** Programming, Raspberry-pi, Embedded-systems, Sensors, HC-SR04

## Measuring Distance With HC-SR04 Sensor

The HC-SR04 sensor is shown in the image below:


| ![containers-view](./imgs/hc_sr04.jpeg)             |
|:---------------------------------------------------:|
|          **Figure: HC-SR04 distance sensor module.**|


The HC-SR04 ultrasonic sensor has two main components: a transmitter (TX) that emits ultrasonic pulses and a receiver (RX) that detects them. It has four pins: Vcc (5V power), GND (ground), TRIG (trigger input to send pulses), and ECHO (output that goes HIGH when a pulse is detected). Common uses include car parking sensors, where they measure distance to nearby objects, and liquid-level monitoring, such as measuring water depth in a tank.

When TRIG is HIGH the sensor sends out ultrasonic pulses. When the ECHO  pin goes HIGH when TRIG is made HIGH, then
transitions to LOW when it detects an ultrasonic pulse [1].

The circuit for this qubit-note is taken from [1] and it shown below:


| ![containers-view](./imgs/hc_sr04_circuit_1.jpeg)   |
|:---------------------------------------------------:|
|    **Figure: HC-SR04 distance sensor module. Image from [1]** | 


| ![containers-view](./imgs/hc_sr04_circuit_2.jpeg)   |
|:---------------------------------------------------:|
|    **Figure: HC-SR04 distance sensor module. Image from [1]** | 


Here is the Python script to run on the Pi

```
"""
Ultrasonic Distance Measurement Example (HC-SR04)
Tested for Raspberry Pi 5
"""

import lgpio
import time

# HC-SR04 pins
TRIG_GPIO = 20
ECHO_GPIO = 21

# Speed of sound (m/s)
VELOCITY = 343

# Timeout values
TIMEOUT_SECS = 0.1
SENSOR_TIMEOUT = -1

# Open GPIO chip
h = lgpio.gpiochip_open(0)

# Configure pins
lgpio.gpio_claim_output(h, TRIG_GPIO)
lgpio.gpio_claim_input(h, ECHO_GPIO)

# Ensure trigger is LOW
lgpio.gpio_write(h, TRIG_GPIO, 0)


def trigger():
    """Send 10µs trigger pulse"""
    lgpio.gpio_write(h, TRIG_GPIO, 0)
    time.sleep(0.000002)

    lgpio.gpio_write(h, TRIG_GPIO, 1)
    time.sleep(0.00001)  # 10 µs

    lgpio.gpio_write(h, TRIG_GPIO, 0)


def get_distance_cms():
    """Measure distance in centimeters"""
    trigger()

    timeout = time.time() + TIMEOUT_SECS

    # Wait for echo HIGH
    while lgpio.gpio_read(h, ECHO_GPIO) == 0:
        if time.time() > timeout:
            return SENSOR_TIMEOUT
    start_ns = time.perf_counter_ns()

    # Wait for echo LOW
    while lgpio.gpio_read(h, ECHO_GPIO) == 1:
        if time.time() > timeout:
            return SENSOR_TIMEOUT
    end_ns = time.perf_counter_ns()

    # Time elapsed (seconds)
    elapsed_seconds = (end_ns - start_ns) / 1_000_000_000 / 2

    # Distance calculation
    distance_m = elapsed_seconds * VELOCITY
    distance_cm = distance_m * 100

    return distance_cm


if __name__ == "__main__":
    try:
        print("Press Ctrl+C to exit")

        while True:
            distance = get_distance_cms()

            if distance == SENSOR_TIMEOUT:
                print("Timeout")
            else:
                print(f"{distance:.2f} cm, {distance / 2.54:.2f} in")

            time.sleep(0.25)  # Do not exceed sensor rate

    except KeyboardInterrupt:
        print("\nExiting...")

    finally:
        lgpio.gpiochip_close(h)

```


----
**Remark**

On the Raspberry Pi 5 the ```pigpio``` does not seem to working at least at the time of writing this post.
The code block above uses ```lgpio``` you can install it on your Pi using

```
sudo apt install python3-lgpio
```

Contray to ```pigpio```, we don't need to run any daemon

----


## Summary

This note explains how to measure distance using the HC-SR04 ultrasonic sensor with a Raspberry Pi 5 and send the measurements over MQTT to another machine. The HC-SR04 has a transmitter (TX) that emits ultrasonic pulses and a receiver (RX) that detects them, with four pins: Vcc (5V), GND, TRIG (trigger input), and ECHO (output that goes HIGH when a pulse is detected). It is commonly used for car parking sensors and liquid-level monitoring. The sensor works by sending pulses when TRIG is HIGH and setting ECHO HIGH until the pulse is detected.


## References

1. Gary Smart, _Practical Python Programming for IoT Build advanced IoT projects using a Raspberry Pi 4, MQTT, RESTful APIs, WebSockets, and Python 3_, Packt Publishing