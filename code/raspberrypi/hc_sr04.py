"""
Ultrasonic Distance Measurement Example (HC-SR04)
Tested for Raspberry Pi 5
"""
import datetime
import lgpio
import time
import paho.mqtt.client as mqtt

# hostname -I on the machine that hosts MQTT
BROKER = "192.168.0.212"
PORT = 1883
ULTRASOUND_TOPIC = "ultrasound"

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

    client = mqtt.Client()
    client.connect(BROKER, PORT, 60)
    try:
        print("Press Ctrl+C to exit")

        while True:
            distance = get_distance_cms()

            if distance == SENSOR_TIMEOUT:
                print("Timeout")
            else:
                print(f"{distance:.2f} cm")

                z_str = json.dumps({"distance": distance,
                                    "unit":"cm",
                                    "timestamp": str(datetime.datetime.now(datetime.UTC))}
                                   )
                client.publish(topic=ULTRASOUND_TOPIC, payload=z_str)


            time.sleep(0.25)  # Do not exceed sensor rate

    except KeyboardInterrupt:
        print("\nExiting...")

    finally:
        lgpio.gpiochip_close(h)