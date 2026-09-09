# qubit-note: Arduino DC Moror Control 

## Overview

In this note we will discuss how control a DC motor via Arduino.
This tuorial assumes an Arduino UNO R4 board. In addition, we will be using an L298N H Bridge.
The following video <a href="https://www.youtube.com/watch?v=dyjo_ggEtVU&t=1s">Controlling DC Motors with the L298N H Bridge and Arduino</a> is a good reference
of what we will be doing in this note.


## Arduino DC Moror Control 

Let's create a small program that controls independently two DC motors. Start the Arduino IDE (you can downlaod the IDE from here: https://www.arduino.cc/en/software/).
In order to control the DC motors we need to use a motor driver. This is because the Arduino usually cannot supply enough current or voltage to drive a DC motor directly.

On the other hand, the motor driver:

- Supplies the motor with enough power.
- Protects the Arduino from voltage spikes.
- Allows you to change the motor's direction.
- Lets you control the motor's speed using PWM.

The table below shows the Arduino pins we will be using in our program.
Left and right are established with respect to the forward direction of the chassis are using.

| L298N | Arduino UNO R4 pin | Purpose                 |
| ----- | -----------------: | ----------------------- |
| ENA   |         **5**      | Left motor speed (PWM)  |
| IN1   |         **7**      | Left direction          |
| IN2   |         **8**      | Left direction          |
| ENB   |         **6**      | Right motor speed (PWM) |
| IN3   |         **9**      | Right direction         |
| IN4   |        **10**      | Right direction         |
| GND   |        **GND**     | Common ground           |

Let's first try the set-up for the left motor. Here is the relevant Arduino code

```
// L298N pins

const int ENA = 5;
const int IN1 = 7;
const int IN2 = 8;


void setup() {
  pinMode(ENA, OUTPUT);
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);

}


void loop() {

  // Motor forward
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);
  analogWrite(ENA, 155);  

 
  delay(1000);

  // Stop the motor
  analogWrite(ENA, 0);

  delay(1000);
}

```

As far as the connections are concerned. Connet the red wire commin from the motor to pin OUT 1 of the L298N H Bridge and the black wire to pin OUT 2.
I am using a  4 AA batteries case which gives 7.4 voltage. I connect the red wire coming out of the case to the 12V pin of the bridge and the black wire of the battery case to
the GND pin of the bridge. We can connect Arduino to the 5V pin of the bridge. In this case we should also connect a GND pin from Arduino to the GND pin of the bridge.
I wont use this option though and plug the USB power supply directly to my laptop as I want to upload code to the board also. Then connect the ENA, IN1 and IN2 pins of the bridge to the
respsctive Arduino boards. Verify the code above and upload it to the UNO board. Make sure before uploading that the circuit is not powered e.g. remove the GND cable coming from the battery case to the bridge.
Once the code is upload put the wire back. You should see the motor rotating.

----
**Remark**

If the motor is not rotating make sure that all the wiring is ok and no loose ends exist. Also make sure that the code is a shown above.


----


Now that we know that our circuit is working, we want to use a more structured way for our progam.
Below is the ```Motor``` class and its associated implementation

```
#ifndef MOTOR_H
#define MOTOR_H

// use all the standard definitions of the Arduino language
#include "Arduino.h"

namespace motors
{
  // class Motor models an electric motor
  // controlled via an L298N bridge.
  class Motor
  {

  public:

    // The default max speed the motor can reach
    static uint8_t default_max_speed(){return 255;}

    // Constructor: Create a motor by passing the forward and backward pins as well
    // as the enable pin. Note that the enable pin must be PWM capable. Finally
    //  there is also an option to set the maximum speed of the motor
    Motor(const char* name, uint8_t in1, uint8_t in2,
          uint8_t enable, uint8_t max_speed=Motor::default_max_speed());

    // Stops the motor
    void stop();

    // Move the motor in the forward direction. This function simply sets the f_pin_ to HIGH and the b_pin_ to LOW
    void forward(const uint8_t speed);

    /// Move the motor in the reverse direction. This function simply sets the f_pin_ to LOW and the b_pin_ to HIGH
    void backward(const uint8_t speed);

    // Returns the id of the forward pin
    uint8_t get_in1_pin()const{return in1_pin_;}

    // Returns the id of the backward pin
    uint8_t get_in2_pin()const{return in2_pin_;}

    uint8_t get_max_speed()const{return max_speed_;}
    bool is_stopped()const{return is_stopped_;}
    uint8_t get_current_speed()const{return current_speed_;};

  private:

    const char* name_;

    // The forward pin
    uint8_t in1_pin_;

    // The backward pin that is the pin for moving the motor
    // in the reverse direction than f_pin_
    uint8_t in2_pin_;

    // The enable pin. It must be PWM capable
    uint8_t enable_pin_;

    // The max speed  the motor is capable of
    uint8_t max_speed_;

    uint8_t current_speed_;

    //flag indicating if the motor is stopped
    bool is_stopped_;

    uint8_t clamp_speed_to_max_(const uint8_t speed);
  };

}//motors

#endif

```

```
#include "motor.h"
#include <Arduino.h>
#include <math.h>

namespace motors
{

  Motor::Motor(const char* name, uint8_t in1, uint8_t in2,
          uint8_t enable, uint8_t max_speed)
  :
  name_(name),
  in1_pin_(in1),
  in2_pin_(in2),
  enable_pin_(enable),
  max_speed_(max_speed),
  current_speed_(0),
  is_stopped_(true)
  {
    //these are output from the Arduino and into
    //the L298N bridge
    pinMode(in1_pin_,OUTPUT);
    pinMode(in2_pin_,OUTPUT);
    pinMode(enable_pin_,OUTPUT);
  }

  void 
  Motor::stop(){
  
    digitalWrite(in1_pin_,LOW);
    digitalWrite(in2_pin_,LOW);
    analogWrite(enable_pin_, 0);
    is_stopped_ = true;
  }

  void 
  Motor::forward(const uint8_t speed){
    
    digitalWrite(in1_pin_, HIGH);
    digitalWrite(in2_pin_, LOW);

    //here speed specifies the duty cycle and should be
    //between [0,255] 0 = always off, 255 = always on
    current_speed_ = clamp_speed_to_max_(speed);
    analogWrite(enable_pin_,current_speed_);
    is_stopped_ = false;
  }

  void 
  Motor::backward(const uint8_t speed){
    digitalWrite(in1_pin_,LOW);
    digitalWrite(in2_pin_,HIGH);

    current_speed_ = clamp_speed_to_max_(speed);
    analogWrite(enable_pin_,current_speed_);
    is_stopped_ = false;
  }

  uint8_t 
  Motor::clamp_speed_to_max_(const uint8_t speed){

    if(speed > 255)
      return max_speed_;

    return speed;

  }

}



```

Below is our updated program:

```
#include "motor.h"

// L298N pins

const int ENA = 5;
const int IN1 = 7;
const int IN2 = 8;

motors::Motor left_motor("left-motor", ENA, IN1, IN2);


void setup() {
  
}


void loop() {

  left_motor.forward(255);

  delay(1000);

  // Stop motor
  left_motor.stop();
  

  delay(1000);

  left_motor.backward(255);

  delay(1000);
}

```





## References

- <a href="https://en.wikipedia.org/wiki/DC_motor">DC Motor</a>
- <a href="https://en.wikipedia.org/wiki/H_bridge">H Bridge</a>
- <a href="https://www.youtube.com/watch?v=dyjo_ggEtVU&t=1s">Controlling DC Motors with the L298N H Bridge and Arduino</a>

