# qubit-note: MPI Series 2/Point-to-Point Communication with MPI


## Overview

When two processes communicate with each other, we call this communication pattern as point-to-point communication [3]. MPI allows for easy information exchange between processes or nodes although the resulting interfaces may be quite overwhelming. In this nnote, I introduce the two most basic point-to-point communication functions in MPI namely ```MPI_Send``` (<a href="https://www.mpich.org/static/docs/latest/www3/MPI_Send.html">doc</a>) and ```MPI_Recv``` (<a href="https://www.mpich.org/static/docs/latest/www3/MPI_Recv.html">doc</a>). 


**keywords** message-passing-interface, MPI, point-to-point-communication

## Point-to-point communication with MPI

```MPI_Send``` performs a blocking send; that is the function call may block until the message is received by the destination process [1]. An ```MPI_Send``` must be matched with a receive operation. ```MPI_Recv``` (<a href="https://www.mpich.org/static/docs/latest/www3/MPI_Recv.html">doc</a>) performs a blocking receive [2]. 

----
**Remark**

Note that ```MPI_Send```  may return before the message is delivered. ```MPI_Send``` uses the so called **standard communication mode** [3]. Behind the scenes, MPI decides whether to block or not based on the size of the message. The blocking lasts until the the destination process collects the message. Thus, if the message is small ```MPI_Send``` returns as soon as the message is copied to a local MPI buffer [3]. This copy is needed in order to release the buffer used by
the source process for subsequent operations, because with this form of send, there
is no way for the sender process to know when the message has been delivered [3].

----

```MPI_Send```  sends a buffer of data of a certain type to another process. It requires the following arguments.

- A pointer to a data buffer
- The datatype contained in the specified data buffer
- How many elements are contained in the buffer 
- A message tag (sort of the id of the message) which should be a non-negative integer
- The receiving process id wihin the communicator
- The communicator used

The datatype must correspond precisely to the data stored in the buffer. For this, MPI has predefined types that can be used. MPI has most of the usual C types. Furthermore, the standard has made provisions for creating and communicating user defined types as well.

Note also that ```MPI_Send``` returns an error value code. If this value is 0 (or the symbolic constant ```MPI_SUCCESS``` ), no error has occurred [3].
The default behaviour when a fatal error occurs in any of the participating processes is to abort the whole execution. In a sense, the default MPI behaviour when an error occurs is not fault tolerant.

```MPI_Recv``` has a very similar signature with ```MPI_Send```. The exception is that there is no destination id parameter but the id of the process from the process receives. Note also that the buffer set aside must be at least as large as the number or elements expected to be received.

Specification of the sent/received datatype is required so that machines wiht different <a href="https://en.wikipedia.org/wiki/Endianness#:~:text=Endianness%20is%20primarily%20expressed%20as,significant%20byte%20at%20the%20largest.&text=Larger%20groups%20comprise%20two%20or,bit%20word%20contains%20four%20bytes.">endianness</a> or machines with different memory types (32-bit, 64-bit, 128-bit) to be able to communicate.

Below is a simple example of how to use ```MPI_Send``` and ```MPI_Recv```. 

```
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
	
	MPI_Status status;
	if(rank == 0){
	
		std::cout<<"Hello from process "<<rank<<" of "<<n_procs<<std::endl;
		int num = 2;
		
		// send a number to the worker 
		MPI_Send(&num, 1, MPI_INT, 1, 0, MPI_COMM_WORLD);
		
		// recv the answer
		int ans = -1;
		MPI_Recv(&ans, 1, MPI_INT, 1, 1, MPI_COMM_WORLD, &status);
		
		if(ans == 0){
			std::cout<<"Number "<<num<<" is odd"<<std::endl;		
		}
		else{
		
			std::cout<<"Number "<<num<<" is even"<<std::endl;
		}
	}
	else if(rank == 1){
	
		// receive 
		int data = -1;
		
		MPI_Recv(&data, 1, MPI_INT, 0, 0, MPI_COMM_WORLD, &status);
		
		if(data % 2 == 0){
			data = 1;
			MPI_Send(&data, 1, MPI_INT, 0, 1, MPI_COMM_WORLD);		
		}
		else{
		
			data = 0;
			MPI_Send(&data, 1, MPI_INT, 0, 1, MPI_COMM_WORLD);
		}
	}
	
	MPI_Finalize();
	// No MPI calls beyond this point
	
	return 0;
}
```

Note the following:

- The tag can be any integer between 0-32767
- ```MPI Recv``` may use for the tag the wildcard ```MPI_ANY_TAG```. This allows an ```MPI_Recv``` to receive from a send using any tag.
- ```MPI_Send``` cannot use the wildcard ```MPI_ANY_TAG```. A speciﬁc tag must be speciﬁed.
- ```MPI_Recv``` may use for the source the wildcard ```MPI_ANY_SOURCE```. This allows an ```MPI_Recv``` to receive from a send from any source.
- ```MPI_Send``` must specify the process rank of the destination. No wildcard exists.


<a href="2021-06-24-object-communication-with-mpi.md">qubit-note: MPI Series 5/ Object Communication with MPI</a> shows how to communicate user defined types
with MPI. <a href="2021-07-08-p2p-communication-modes-with-mpi.md">qubit-note: MPI Series 4/ P2P Communication Modes with MPI</a> discusses further communication modes for P2P transactions with MPI.

## References

1. <a href="https://www.mpich.org/static/docs/latest/www3/MPI_Send.html">MPI_Send</a>
2. <a href="https://www.mpich.org/static/docs/latest/www3/MPI_Recv.html">MPI_Recv</a>
3. Gerassimos Barlas, _Multicore and GPU Programming An Integrated Approach_, Morgan Kaufmann