# qubit-note: P2P Communication Modes with MPI

## Overview

<a href="2021-07-07-point-to-point-communication-with-mpi.md">qubit-note: Point-to-Point Communication with MPI</a>
used ```MPI_Send``` and ```MPI_Recv``` to enable communication between to pocesses in communication groupt. 
In this note, I want to expand on this and discuss a few more communication modes supportd by the MPI standard.
Specifically,

- Buffered
- Synchronous
- Ready

## P2P communication modes with MPI

MPI has three additional modes for P2P communication [1]:

- Buffered
- Synchronous
- Ready

In the buffered mode, the sending operation is always locally blocking and just like with standard communication mode, it will return as soon as the message is copied to a buffer. 
The difference here is that the buffer is user-provided [1]. In contrast, the synchronous mode is a globally blocking operation; the sending operation will return only when the retrival of the message has been initiated by the receiving process. However, the message receiving may not be completed [1]. 
These two modes are somehow symmetric;  in the buffered mode we trade the waiting with memory whilst in the synchronous mode we don't mind  waiting for the message to reach the destination.

In the ready mode, the send operation will succeed only if a matching receive operation
has already been initiated [1]. If this is not the case, the function returns with an error code.
The purpose of this mode is to reduce the overhead of handshaking operations [1].

So how can we distinguish between these different commnunication modes? 
This is done by prefixing the initial letter of each mode before the ```Send``` [1]. Thus, we have

- ```MPI_Bsend```
- ```MPI_Ssend```
- ```MPI_Rsend```

The resr of the functions signatures is the same as that of ```MPI_Send```:

```
int [ MPI_Bsend | MPI_Ssend | MPI_Rsend ] (void∗ buf , int count , 
                                           MPI_Datatype datatype , 
                                           int dest , int tag , MPI_Comm comm ) ;

```

Finally, note that blocking sends can be matched with non blocking receives,
and vice versa. The crucial parts that need to match are the endpoints, as identified
by the (communicator, rank, message tag) tuple.

## References

1. Gerassimos Barlas, _Multicore and GPU Programming An Integrated Approach_, Morgan Kaufmann

