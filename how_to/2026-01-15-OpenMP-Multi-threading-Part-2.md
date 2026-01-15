# qubit-note: Parallel Computing Series | OpenMP Multi-threading Part 2

## Overview

<a href="2026-01-10-OpenMP-Multi-threading-Part-1.md">qubit-note: Parallel Computing Series | OpenMP Multi-threading Part 1</a> introduced OpenMP as
a mutlti-threading programing paradigm. In this note we will discusss some synchronization primitives available.


## OpenMP Multi-threading Part 2

Very often, when developing mutlti-threading software, we want and operation to be performed by one thread only or an operation should
be performed by a thread and when the performing thread finishes another thread can take over. These are operations that require
some sort of synchronization. We will will look into the following OpenMP constructs

- ```omp master```
- ```omp single```
- ```omp shared```
- ```omp critical```

Let's start with ```omp single```

#### omp single

Executes a block of code by exactly one thread in a parallel region. It is useful when:


-Initialization
- I/O
- Creating shared data structures
- Tasks creation

Below there is an example of initializing a shared vector

```
#include <iostream>
#include <vector>
#include <omp.h>

int main()
{
    std::vector<int> data;

    #pragma omp parallel
    {
        // Only ONE thread executes this
        #pragma omp single
        {
            std::cout << "Single thread: " << omp_get_thread_num() << "\n";
            data.resize(10);
            for (int i = 0; i < 10; ++i)
                data[i] = i * i;
        } // All threads wait here (implicit barrier)

        #pragma omp for
        for (int i = 0; i < data.size(); ++i)
        {
            printf("Thread %d sees data[%d] = %d\n",
                   omp_get_thread_num(), i, data[i]);
        }
    }

    return 0;
}

```

#### omp masked

```omp masked``` is a newer OpenMP construct (introduced in OpenMP 5.0) that is often misunderstood because it looks similar to ```single``` and ```master```, but it serves a different purpose.
```omp masked``` executes a block of code only on threads that satisfy a mask. By default, only the master thread (thread 0) executes it. There is no implicit barrier at the end.
esigned mainly for tasking and accelerator/offload scenarios

```
#include <omp.h>
#include <iostream>

int main()
{
    #pragma omp parallel
    {
        #pragma omp masked
        {
            std::cout << "Masked executed by thread "
                      << omp_get_thread_num() << "\n";
        }

        std::cout << "Thread " << omp_get_thread_num()
                  << " continues\n";
    }
}

```

Why ```masked``` exists

master has problems:

Only thread 0 executes

Cannot safely create tasks in many cases

Not compatible with some offloading models

masked replaces master in modern OpenMP.

OpenMP 5+ recommendation:
Use masked instead of master.


```
#include <omp.h>
#include <cstdio>

int main()
{
    #pragma omp parallel
    {
        #pragma omp masked
        {
            for (int i = 0; i < 4; ++i)
            {
                #pragma omp task
                {
                    printf("Task %d executed by thread %d\n",
                           i, omp_get_thread_num());
                }
            }
        }
    }
}

```

## Summary

## References
