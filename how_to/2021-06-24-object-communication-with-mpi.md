# qubit-note: Object Communication with MPI

## Overview

In object oriented code bases, data is typically organized into classes that wrap functionality, hide information and expose an API so that client code can utilize them. 
Thus, frequently, we end up in the situation where we have an object that we need to send across another process. MPI offers various posibilities to do so. 
In this note we will see  ```MPI_Type_create_struct```. This is the most generic of the available functions,
allowing the use of blocks made of different datatypes [1]


**keywords** message-passing-interface, MPI, object-communication


## Object communication with MPI

MPI communication functions such as ```MPI_Send/Recv``` need as an input the type of the data that is to be communicated [1]. When dealing with primitive types like integers and floats MPI has got us covered so there isn't much we should do. 

However, frequently we want to communicate structures or objects. Sure, we can break up the structures
that need to be communicated into individual elements or arrays of elements and send these
in a series of send operations. However, this costly and rather counter productive; it breaks data encapsulation to start with. 

Why it is costly, can be understood by considering the so-called start-up latency [1]. This is the fixed cost we need to accept that includes the activation of multiple
OS layers, the network interface, and so on [1]. The result is that although the actual over-the-wire
times may be identical, the accumulation of the extra start-up latencies makes such an approach expensive to use. 

MPI has two main mechanisms that we can use to communicate structures between
heterogeneous machines [1]:

- MPI derived datatypes
- Packing/unpacking data

In this post, we will look into how to construct MPI derived datatypes using  ```MPI_Type_create_struct``` and leave the second approach for another post.

### Derived datatypes

The memory layout of the same data structure differs from machine to machine. MPI, in order to successfully transfer and  translate   an instance of a structure from one machine to another, it requires the following information [1]: 

- The number and types of all the data members/fields.
- The relative offset of the fields from the beginning of the structure (where to deposit data).
- The total memory occupied by a structure, including any padding necessary to align it to specific boundaries. This is needed so that arrays of structures can be communicated.

MPI provides utilities for describing the 
information above for a generatl datatype. Once a derived datatype is defined, a reference to this object can be used in any communication function that requires a datatype specification parameter [1].


----
**Remark**

Derived datatypes must be declared individually/locally in all the processes that will
employ them [1].

----

Two of the most commonly used functions for creating derived datatypes are [1]:

- ```MPI_Type_vector```
- ```MPI_Type_create_struct```

```MPI_Type_vector``` is useful  for
extracting blocks of data from single or multidimensional arrays of a single datatype e.g. a vector.
```MPI_Type_create_struct``` is the most generic of the available functions,
allowing the use of blocks made of different datatypes [1]. 

Regardless of the approach used, each specification of a derived datatype must be followed by a call to the
```MPI_Type_commit``` function for having MPI store the specification internally. Once
a datatype is committed, it can be used repeatedly in communication functions.
```MPI_Type_commit``` takes just a single parameter, which is a reference to the
```MPI_Datatype``` object [1].

The following example shows how to use ```MPI_Type_create_struct```.

```
#include <mpi.h>
#include <iostream>


struct Point
{
 unsigned int id;
 double x;
 double y;
};
```

As already mentioned  ```MPI_Type_create_struct``` is rather involved so we group everything in the following function:

```
void create_mpi_point(	MPI_Datatype* t){

	Point p;
	
	// the types the struct has
	MPI_Datatype types [3];
	
	types[0] = MPI_UNSIGNED;
	types[1] = MPI_DOUBLE;
	types[2] = MPI_DOUBLE;
	
	// get the addresses
	MPI_Aint displ[3];
	MPI_Aint off; 
	MPI_Aint base;
	
	displ [0] = 0 ;
	
	MPI_Get_address (&(p.id) , &base ) ;
	MPI_Get_address (&(p.x) , &off ) ;
	displ [1] = off- base ;
	MPI_Get_address (&(p.y) , &off ) ;
	displ [2] = off - base;
	
	int blklen [3] = {1, 1, 1} ;
	
	// create the type
	MPI_Type_create_struct( 3 , blklen , displ , types , t);
	
	// commit it
	MPI_Type_commit ( t ) ;

}
```

Here is the main function:

```
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
	
	if(n_procs > 2){
		std::cout<<"Application should be run with 2 processes."<<std::endl;
		MPI_Abort(MPI_COMM_WORLD, EXIT_FAILURE);
	}
	
	// status on the receive side
	MPI_Status status;
	
	// all processes must commit the Point type
	MPI_Datatype mpi_point_type;
	
	// create the mpi point
	create_mpi_point(&mpi_point_type);
	
	if(rank == 0){
	
		std::cout<<"Hello from process "<<rank<<" of "<<n_procs<<std::endl;
		
		Point p = {10, 0.5, 1.5};
		
		std::cout<<"Process "<<rank<<" sending point "
		         <<p.id
		         <<", "
		         <<p.x
		         <<", "
		         <<p.y
		         <<std::endl;
		
		// send a number to the worker 
		MPI_Send(&p, 1, mpi_point_type, 1, 0, MPI_COMM_WORLD);
			
	}
	else if(rank == 1){
	
		// receive 
		Point p_recv;
		
		MPI_Recv(&p_recv, 1, mpi_point_type, 0, 0, MPI_COMM_WORLD, &status);
		
		std::cout<<"Process "<<rank<<" received point "
		         <<p_recv.id
		         <<", "
		         <<p_recv.x
		         <<", "
		         <<p_recv.y
		         <<std::endl;
			
	}
	
	
	
	MPI_Finalize();
	// No MPI calls beyond this point
	
	return 0;

}
```

## References

1. Gerassimos Barlas, _Multicore and GPU Programming. An Integrated Approach_.
