# qubit-note: Parallel Computing Series | OpenMP Part 3 | Parallelization of for Constructs

## Overview

In this qubit-note we will look into how to parallelize for loops using OpenMP. The loop construct arises very
frequently in sceintific applications e.g. when assembling the matric contributions in an FEM simulation.
OpenMP provides a very easy way to parallelize such loops

**keywords** openmp, synchronization, c++, programing

## OpenMP Multi-threading Part 3

Let's assume for a moment that the application's memory requirements can be satisifed on a single node. Let's further assume that the
expensive part is some expensive for loops. The parallel for OpenMP construct is an ideal candidate to speed up such an application. 
Below is an example that illustrates how to use the parallel for construct in OpenMP:

```
#include <iostream>
#include <vector>
#include <omp.h>

int main() {
    const int n = 1'000'000;

    std::vector<double> a(n), b(n), c(n);

    #pragma omp parallel
    {
        // Only the master thread executes this (no implicit barrier)
        #pragma omp master
        {
            int num_threads = omp_get_num_threads();
            std::cout << "Number of threads: " << num_threads << std::endl;
        }

        // One arbitrary thread initializes the vectors
        #pragma omp single
        {
            for (int i = 0; i < n; i++) {
                a[i] = i * 1.0;
                b[i] = i * 2.0;
            }
        }

        // Implicit barrier at end of single ensures init is done

        // Parallel vector addition
        #pragma omp for
        for (int i = 0; i < n; i++) {
            c[i] = a[i] + b[i];
        }
    }

    std::cout << "c[10] = " << c[10] << std::endl;
    return 0;
}

```

The program uses two of the constructs we saw in <a href="/2026-01-15-OpenMP-Multi-threading-Part-2.md">qubit-note: Parallel Computing Series | OpenMP Multi-threading Part 2</a>
namely ```omp mster``` and ```omp single```. In this section we are interested in the ```omp for``` construct. So how work sharing is achieved in OpenMP ```omp for``` construct?

`#pragma omp for` achieves work sharing by dividing the iteration space into chunks and then assigns each of these  chunks to the threads in the current parallel team
There is also an implicit barrier at the end of the construct. All of this is done by the OpenMP runtime, not us. It is no surprise therefore why OpenMP has seen
much popularity when it comes to optimizing performance for applications dominated by for loops. There are various policies how to assign iterations to threads:

**static**
This is the default policy. Iterations are divided contiguously and as evenly as possible. Iterations are assumed independent and therefore each thread can execute
independent of the others. Notice that the loop index is private and unque per thread.

**dynamic**

Static scheduling is good when work can be evenly divided among the threads. However, this is not always the case.
In the dynamic policy, threads request chunks on the fly. This is benetificial when dealing with uneven workloads. However, the overhead is in general higher. 


**guided**

A balance between the dynamic and static policies is the guided policy. in this policy the large chunks will go first followed by the  smaller 


In order to ```omp for``` to work, our progam has to respect certain rules [1]:

- The loop index variable must be an integer
- The loop must have standard exist conditions 
- The loop index cannot be modified in the loop
- The loop iterations must be countable
- The loop must not have any loop-carried dependencies


## Summary


This note introduces how to parallelize `for` loops using OpenMP, which is especially useful for scientific computing workloads like FEM matrix assembly where loops dominate runtime. When memory fits on a single node and computation is loop-heavy, OpenMP’s `parallel for` construct offers an easy performance boost.

The core idea of `#pragma omp for` is work sharing: the OpenMP runtime splits the loop iteration space into chunks and assigns them to threads automatically. An implicit barrier at the end ensures all threads finish before continuing.

The note also explains loop scheduling policies:

- static (default): iterations are evenly and contiguously divided among threads; low overhead, best for balanced workloads
- dynamic: threads request work chunks at runtime; useful for uneven workloads but with higher overhead
- guided: a hybrid approach where large chunks are assigned first, then smaller ones to improve load balance

Finally, it lists the requirements for using `omp for`:

- The loop index must be an integer and private to each thread
- The loop must have a standard, countable structure
- The loop index must not be modified inside the loop
- There must be no loop-carried dependencies


## References

1. Robert Robey, Yulian Zamora, _Parallel and High Perfromance Computing_, Manning Publications.
