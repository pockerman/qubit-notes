# qubit-note: Parallel Computing Series | OpenMP  Part 1 | Introduction

## Overview

When lloking at improving the performance of a software system, using threading is one of solutions.
However, given the shared memory that is asusmed by this progamming model, the details become a critical factor.

In this qubit note we will introduce <a href="https://www.openmp.org/">OpenMP</a>. This is one of the most widedly supported open standards
for threads parallelism and shared memory programming

**keywords** Programming, OpenMP, Mutli-threading, Shared-memory-programming, C++

## OpenMP Multi-threading Part 1

In this qubit note we will introduce a few functions from the OpenMP API, how to compile an OpenMP based program and how to
set the number of threads. 

The code below is asimple C++ driver that queries the thread id and the number of threads utilised. This id done
using ```omp_get_thread_num``` and ```omp_get_num_threads```

```
#include <iostream>
#include <omp.h>

int main()
{
  
 
  auto n_threads = omp_get_num_threads();
  auto thread_id = omp_get_thread_num();

  std::cout << "Number of threads: " << n_threads << std::endl;
  std::cout << "Thread ID: " << thread_id << std::endl;
  return 0;
}
```

Build the code using

```
g++ -fopenmp -o main main.cpp
```
This should print

```
Number of threads: 1
Thread ID: 0
```

Notice the following

- We need to include the header ```<omp.h>``` in order to have access to the API
- OpenMP functions start with ```omp_```
- Thread ids in OpenMP start with zero

Let's try to increase the number of threads used by the driver above. We have two ways to do this

- Set the environment variable ```export OMP_NUM_THREADS```
- Use ```omp_set_num_threads```

The program below shows the changes. We also had to insert a parallel region using ```#pragma omp parallel``` otherwise querying the number
of threads would return 1. That is we need to be in a parallel region in order to correctly find the number of threads available.

```
#include <iostream>
#include <omp.h>


int main()
{

  // set number of threads
   omp_set_num_threads(4);

  #pragma omp parallel
  {
    auto n_threads = omp_get_num_threads();
     auto thread_id = omp_get_thread_num();

     std::cout << "Number of threads: " << n_threads << std::endl;
     std::cout << "Thread ID: " << thread_id << std::endl;
  }
 return 0;
}
```

Run the program will a produce an output like the following.

```
Number of threads: Number of threads: 4
Thread ID: 0
Number of threads: 4
Thread ID: 1
Number of threads: 4
Thread ID: 3
4
Thread ID: 2

```

Note that the order may be different in your machine. Alos note how the output is rather interwinded. The standard output is a shared resource that all threads
compete to have access to. We will see how to remedy this using critical sections.

## Summary

This qubit-note introduces OpenMP as a widely supported standard for shared-memory multithreaded programming, focusing on basic concepts and usage to improve software performance. It explains how to compile OpenMP programs, query thread IDs and thread counts using the OpenMP API. The note demonstrates that OpenMP functions report a single thread unless executed inside a parallel region, and shows how to create such a region with ```#pragma omp parallel```. It also covers two ways to control the number of threads—via the ```OMP_NUM_THREADS``` environment variable or the ```omp_set_num_threads``` function—and illustrates how parallel execution can lead to interleaved output due to shared resources like standard output, motivating the need for synchronization mechanisms such as critical sections.

## References

1. <a href="https://www.openmp.org/">OpenMP</a>
2. Robert Robey, Yulian Zamora, _Parallel and High Perfromance Computing_, Manning Publications.
