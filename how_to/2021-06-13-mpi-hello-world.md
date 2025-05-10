# qubit-note: MPI Hello World


## Overview

The <a href="https://en.wikipedia.org/wiki/Message_Passing_Interface">Message Passage Interface</a>, or MPI for short, is perhaps the defacto standard used in nowadays scientific distributed computing. It provides interfaces for both point-to-point and collective communication. 
In this short note, I show how to write a very basic C++ driver using MPI.



## MPI Hello World

MPI is a well-established standard that includes [1]: 

- Process creation 
- Process management
- Point-to-point communication
- Collective communication
- One-sided communication
- External interfaces
- Topologies

Language bindings exist for C and Fortran. Newer MPI standards are trying to better support the scalability in future extreme-scale computing systems, because currently, the only feasible option for increasingthe computing power is to increase the number of cooperating processors [1]. 

The following code snippet is the ```Hello World``` equivalent for MPI. It demonstrates basic usage of the standard. 

```
// example_1.cpp

#include <mpi.h>
#include <iostream>

int main(int argc, char** argv){

	int rank;
	int n_procs;
	
	// initialize MPI. No MPI calls
	// prior to this point should be made
	MPI_Init(&argc, &argv);
	
	// what's my rank
	MPI_Comm_rank(MPI_COMM_WORLD, &rank);
	
	// how may procs
	MPI_Comm_size(MPI_COMM_WORLD, &n_procs);
	
	std::cout<<"Hello from process "<<rank<<" of "<<n_procs<<std::endl;
	
	MPI_Finalize();
	// No MPI calls beyond this point
}
```

We can compile the code by using the following:

```
mpicxx example_1.cpp -o example_1
```

Executing using four processes:

```
mpirun -np 4 example_1
```

produces:

```
Hello from process 0 of 4
Hello from process 1 of 4
Hello from process 3 of 4
Hello from process 2 of 4

```

The ```mpirun``` command is also known as ```mpiexec``` on some implementations. A few things to notice are:

- In order to access any MPI  related functionality we need to inlude the header file ```mpi.h````
- MPI related functions start with the prefix ```MPI_```
- As commented in the code, all MPI related calls should occur within ```MPI_Init/MPI_Finalize```. 

In the code above, every process executes the same instructions. We can use ```if/else``` statements to differentiate what each process will execute. The variable ```MPI_COMM_WORLD``` is a predefined intra-communicator, i.e., it serves communications taking place between processes belonging to its own group of processes [1]. 
The code above also calculates the rank of the calling process via ```MPI_Comm_rank```, and the total number of processes in the comunicator ```MPI_Comm_size```.

The note <a href="2021-07-07-point-to-point-communication-with-mpi.md">qubit-note: Point-to-Point Communication with MPI</a> shows some basic point-to-point communication 
with MPI.


## References

1. Roman Trobec et al., ```Introduction to parallel computing. From algorithms to programming on state-of-the-art platforms```, Springer.