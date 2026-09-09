# qubit-note: High Performance Computing | Race Conditions

## Overview

A data race condition is a situation where two or more running elements, such as threads and
goroutines, try to take control of or modify a shared resource or shared variable of a program.
Strictly speaking, a data race occurs when two or more instructions access the same memory
address, where at least one of them performs a write (change) operation. If all operations are read
operations, then there is no race condition. In practice, this means that you might get different
output if you run your program multiple times, and that is a bad thing.