# qubit-note: Electronic Circuits 101

## Overviw

In this note we will look into <a href="https://en.wikipedia.org/wiki/Electronic_circuit">electronic circuits</a>. 
We will also going to discuss current, voltage and resistors. Finally, we will look into <a href="https://en.wikipedia.org/wiki/Breadboard">breadboards</a>.
We will keep the discussion brief as always.

**keywords** electronic-circuits, current, voltage, resistors


## Electronic circuits 101

Ok so what is an electronic circuit? An electronic circuit combines various electronic components such as
resistors, transistors, current sources to achieve a spcific function. Circuits can be as simple as
a circuit that turns on/off a torch or as complex as a circuit that controls a CPU. Regardless of the 
complexity of the circuit, all are built based on the same principles.

The most elementary of these principles and the one that you are probably aware of, is that for a circuit
to perform it's task there must be a complete connected path between its components.
So for a circuit that includes a battery, there must be a complete path starting from the positive (+) side of the
battery, through any components (such as a switch and buzzer), and then back to the negative (-) side of the
battery.  When the switch is closed (turned on), the circuit is complete,
allowing current to flow around the circuit, and the buzzer will sound. When the switch is open (off ), there is
a gap between the connections inside the switch preventing the current flow and causing the buzzer to stop.

We have two types of circuits; analog and digital that we will discuss in another note.

Let's now look into three fundamental concepts regarding electronic circuits; current, voltage and resistors.
We will see that there is a relationship among them expressed by <a href="https://en.wikipedia.org/wiki/Ohm%27s_law">Ohm’s law</a>

### Voltage, current and resistors


#### Voltage

According to wikipedia:

_Voltage, also known as (electrical) potential difference, electric pressure, or electric tension, is the difference in electric potential between two points.._

In other words, the <a href="https://en.wikipedia.org/wiki/Voltage">voltage</a> is the difference in energy between two terminals or points in a circuit. It is measured in
volts indicated by a letter $V$. For example a 9V battery should indicate a 9V between its poles when using a voltometer. Note that the actual indication may vary depending
on how much charge is in the battery and what load is connected to it

----
**Remark**

A voltmeter is an instrument used to measure the electric potential difference, or voltage, between two points in an electrical circuit.  
It is always connected in parallel with the component or circuit section being measured to avoid disrupting the current flow.

----


#### Electric current

According to wikipedia:

_An electric current is a flow of charged particles, such as electrons or ions, moving through an electrical conductor or space. It is defined as the net rate of flow of electric charge through a surface..._


In layman's terms, <a href="https://en.wikipedia.org/wiki/Electric_current">electric current</a> is the flow of electric charge around a circuit. 
Current is measured in amperes. This is normally abbreviated to amps and its value is indicated by a letter $A$. 

----
**Remark**

Electric current is related to voltage: the higher the voltage of the power supply, the more current is able to flow through the circuit.
We use various components such as resistors and voltage dividers to regulate the amount of electricity that flows within a circuit.

----

When discussing electronic circuits, we will indicate electric current with the letter $I$.


#### Resistors


The electrical resistance is a measure of how difficult it is for the current to flow around a circuit. It is
measured in ohms. The value ohms is represented by the Greek leter $\Omega$. There is resistance
in all components of a circuit, but you can normally disregard the small amount of resistance in a good
conductor such as a wire. 

As mentioned above, there is arlationship among volatge, resistors and electric current given by Ohm’s law:

$$
I = \frac{V}{R}
$$

So this formula says that to find the current through a circuit, divide the voltage by the resistance. This
can be rearranged to find the voltage or the required resistor size.


### Breadboard

Let's now look into one essential element that we will use when developing electronic circuits namely the breadboard or plugboard
A breadboard is a good way of creating temporary circuits to allow testing prior to committing with solder.
It’s a plastic board with internally connected rows of holes that let components and wires connect without soldering, making it easy to modify or reuse circuits. 
Solid core or jumper wires are used because flexible multi-stranded wire doesn’t fit properly.

Breadboards come in many sizes and can sometimes be joined together, though compatibility depends on the manufacturer. 
Different sizes suit different projects, but a half-size breadboard is often ideal, especially for use with a Raspberry Pi.

Internally, the central area is arranged in numbered columns and lettered rows, with each column split in the middle. Power rails usually run along the top and bottom and are used for ground and positive voltage, though some boards have breaks in these rails that must be checked. Layout details can vary between models, but connectivity is what matters most.

Mounting plates that hold a Raspberry Pi and a breadboard together are a helpful accessory, making wiring more stable and easier to manage.


## Summary

This qubit note introduces the basics of electronic circuits and their key components. Electronic circuits are combinations of components that must form a complete path for current to flow, whether the circuit is simple or complex. 

We also discussed three fundamental concepts: voltage, current, and resistance. Voltage is described as the electrical potential difference between two points, current as the flow of electric charge, and resistance as how much a circuit opposes that flow. Their relationship is summarized by Ohm’s law, which shows how current depends on voltage and resistance.

Finally, we introduced breadboards as essential tools for building and testing temporary circuits without soldering.


## References

1. <a href="https://en.wikipedia.org/wiki/Electronic_circuit">Electronic circuit</a>
2. <a href="https://en.wikipedia.org/wiki/Breadboard">Breadboard</a>
3. <a href="https://en.wikipedia.org/wiki/Ohm%27s_law">Ohm’s law</a>
4. <a href="https://en.wikipedia.org/wiki/Voltage">Voltage</a> 
5. <a href="https://en.wikipedia.org/wiki/Electric_current">Electric current</a>