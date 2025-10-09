# qubit-note: MPI Series 1/MPI Hello World


## Overview

The <a href="https://en.wikipedia.org/wiki/Message_Passing_Interface">Message Passage Interface</a>, or MPI for short, is perhaps the de facto standard used nowadays in scientific distributed computing.
In fact, the terminology used by ```torch.distributed``` is based on the terminology in the MPI [3]. The MPI standard provides interfaces for both point-to-point and collective communication. 
In this qubit  note, I will  write a very basic C++ driver using MPI and discuss some basic terminology.

**keywords** message-passage-interface, high-performance-computing, c/c++

## MPI Hello World

MPI is a well-established standard that includes [1]: 

- Process creation 
- Process management
- Point-to-point communication
- Collective communication
- One-sided communication
- External interfaces
- Topologies

Language bindings exist for C and Fortran. Newer MPI standards are trying to better support the scalability in future extreme-scale computing systems, because at the time of writing, the only feasible option for increasing the computing power is to increase the number of cooperating processors [1]. 

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

This produces:

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

## Summary

In this short post, we saw how to write a basic Hello World example using MPI. Nevertheless, this example allowed us to introduce some basic terminology such as ```MPI_COMM_WORLD```
and how to access the total number of processes as well as the id of the process we are looking into. 

MPI is not the only standard for distributed computing. Other standards for this task are <a href="https://github.com/pytorch/gloo">gloo</a> a collective communications library with various primitives for multi-machine training on CPUs and <a href="https://github.com/NVIDIA/nccl">nccl</a> by NVIDIA targeting collective multi-GPU communication.

## References

1. Roman Trobec et al., _Introduction to parallel computing. From algorithms to programming on state-of-the-art platforms_, Springer.
2. <a href="https://docs.pytorch.org/docs/stable/distributed.html">Distributed communication package - torch.distributed</a>
3. Luca Antiga, Eli Stevens, Howard Huang, Thomas Viehmann, _Deep Learning with PyTorch_, 2nd Edition, Manning.