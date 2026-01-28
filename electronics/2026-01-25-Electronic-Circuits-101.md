# qubit-note: Electronic Circuits 101

## Overviw


An electronic circuit combines individual electronic components to perform a specific function. This
could be as simple as a light circuit in a torch/flashlight that turns on when the on switch is pressed or
incredibly complex such as the circuitry inside a laptop computer. Electronic circuits are all built around the
same principles.
The most basic principle is the concept that an electronic circuit must make a complete physical circuit.
So for a circuit that includes a battery, there must be a complete path starting from the positive (+) side of the
battery, through any components (such as a switch and buzzer), and then back to the negative (-) side of the
battery. This is shown in the circuit in Figure 1-1.

This is a simple circuit connected using crocodile clip leads. The circuit has a buzzer and a switch,
which can turn the buzzer on and off. When the switch is closed (turned on), the circuit is complete,
allowing current to flow around the circuit, and the buzzer will sound. When the switch is open (off ), there is
a gap between the connections inside the switch preventing the current flow and causing the buzzer to stop.
Obviously this is a very basic circuit, but it’s also the basis of almost all the circuits you’ll make. You will
replace the mechanical switch with an electronic component and use different sensors to turn the switch on
and off. You will also use different outputs, including LEDs and motors.

I’m going to keep the theory as simple as possible, but voltage, current, and resistance are some terms that I use
throughout the book. Understanding how the circuit works and the math involved is going to be important by
the time you get to the stage where you are designing your own circuits. I have avoided putting too much math
into the projects, but there are some worked examples that you may find useful in future.
The voltage is the difference in energy between two terminals or points in a circuit. It is measured in
volts indicated by a letter V. For example, you could have a 9V PP3 battery such as the one used in the buzzer
circuit in Figure 1-1. The battery has a difference of 9 volts between its positive and negative terminals. We
would consider the negative terminal to be at 0 volts and the positive terminal at 9 volts. The 0V connection
is considered the ground terminal with voltages relative to that point. Although the battery is designed for 9V,
the actual voltage may vary depending on how much charge is in the battery and what load is connected to it.
The current is the flow of electric charge around a circuit. Current is measured in amperes. This is
normally abbreviated to amps and its value is indicated by a letter A. The current is related to the voltage: the
higher the voltage of the power supply, the more current is able to flow through the circuit, although it also
depends on what other components are in the circuit. Using conventional electric current, you say that the
current flows from the positive to the negative terminal. In the electronic circuits you’ll create, most currents
will be small and so will normally be measured in milliamps (mA), where 1mA = 0.001A.


The electrical resistance is a measure of how difficult it is for the current to flow around a circuit. It is
measured in ohms. The value ohms is represented by the Greek omega character (Ω). There is resistance
in all components of a circuit, but you can normally disregard the small amount of resistance in a good
conductor such as a wire. The resistors you will be using normally range from around two hundred ohms to
several thousand ohms (kΩ).

This relationship was discovered by German scientist Georg Ohm
and is known as Ohm’s Law. The basic formula is this:
I = V/R
As you may expect, V represents voltage and R represents resistance (measured in ohms), but I is not so
obvious. I is used to indicate current, based on the French phrase, “intensité de courant”.1
So this formula says that to find the current through a circuit, divide the voltage by the resistance. This
can be rearranged to find the voltage using this formula:
V=IxR
To calculate the required resistor size, use:
R = V/I


The world we live in is varied. If we take sound as an example, we may use various words to describe
the amount of sound something is making, from saying that someone is very quiet, or that the MP3
player is very loud, or even that a pneumatic drill is deafening. We don't normally know or care about
the actual values of the sound (measured in decibels), but we do know if we want it to be louder or
quieter. A computer however does not understand these terms. It only deals in actual values. In fact, at
a most basic level, it only thinks of things being on and off, but it can compare against different levels to
interpret this as a more accurate value.
An analog circuit can interpret any number of variations of the input. Perhaps one of the few remaining
purely analog circuits you will find at home today is a simple amplifier built into a set of speakers. Here,
as you turn the volume control clockwise, the volume smoothly increases compared to the input signal.
Compare this to a modern TV, where you press the volume button on the remote control and the volume
moves up a fixed amount, say between 1 and 40.
Most electronic circuits are now digital and in fact most include some kind of micro-processor, either
a full computer such as a Raspberry Pi or a more basic micro-controller such as the ATMega micro-
controllers used in the Arduino. The real world continues to be analog, so there is often an analog sensor
or output and an element of conversion between analog and digital and vice versa.


Breadboard
Many of the circuits in this book are built on a solderless breadboard, sometimes called a plugboard. A
breadboard is a good way of creating temporary circuits to allow testing prior to committing with solder.
They consist of a plastic board with a matrix of holes. The holes are then connected in small rows so that
components plugged into the same section are connected.
Breadboards are very easy to use and don’t damage the components, so it’s easy to change the circuit
and experiment with different components. If you don’t want the circuit any more, then the components can
be removed and both the breadboard and the components can be used again for another circuit. Integrated
circuits (ICs) can be also be inserted and wired to other components. To connect wires to a breadboard,
you should use solid core wire or special jumper wires that have a solid end that can be plugged into the
breadboard. The alternative type of wire is known as multi-stranded wire and it’s more flexible and so more
popular with soldered circuits, but it doesn’t plug into the breadboard properly.
Breadboards are available in a variety of sizes, from small ones with 170 holes to large boards with
multiple breadboards mounted onto a single panel. You can also connect multiple boards together, which
slot together. Unfortunately, there is no standard for how the boards slot together, so this may work only if
you’re using the same manufacturer. A selection of different breadboards is shown in Figure 1-3.

Each size of breadboard has a set of circumstances in which it works best. The smallest can be included
in a small box, whereas the large one is great for larger circuits and includes connectors that are useful for
plugging banana plugs from an external power supply.
For most of the circuits in this book, the half-size breadboard is an ideal size. It’s about the same size as
the Raspberry Pi and is a good compromise between the space taken up and the amount of space needed for
connecting circuits. An example of the half-size breadboard layout is shown in Figure 1-4.

The main central area consists of columns numbered 1 to 30 and rows from a to l. Each of the
columns is connected with a break down the center. So for column 1 positions a to f are connected and
then positions g to l. There are then two rows at the top and bottom of the breadboard, which depending
on the manufacturer, may be included or as an optional extra. These rows are normally used for the main
power rails, with the blue row used as ground as the red row used for the positive rail. Also note that on this
example the red line covers 12 holes with there being a break in the line between the next 12. This indicates
that there is also a break in the track at that point, so if you’re using a single supply voltage, you may want
to use a short wire to connect these together. This very much depends on the manufacturer, so you should
check the ones that you have. It’s frustrating trying to understand why your circuit isn’t working and then
finding out it’s because that particular breadboard has a gap in the power rail. On the circuits in this book,
I have assumed that there is no break in the power rails.
You may also notice that some breadboards have a slightly different number of pins (many have only
10 rows between a and j) and are numbered in a different direction. The actual positioning doesn’t matter as
long as the same pins are connected.
A useful addition is a mounting plate that allows a Raspberry Pi and a half-size breadboard next to each
other. An example is shown in Figure 1-5. The mounting plate make it easier to wire the Raspberry Pi and
breadboard together, as it means the wires are less likely to fall out. You could even make your own using an
appropriately sized piece of plastic or thin wood.
## Summary

## References