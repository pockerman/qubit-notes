# qubit-note: Parallel Computing Series | OpenMP Multi-threading Part 2

## Overview

<a href="2026-01-10-OpenMP-Multi-threading-Part-1.md">qubit-note: Parallel Computing Series | OpenMP Multi-threading Part 1</a> introduced OpenMP as
a mutlti-threading programing paradigm. In this note we will discusss some synchronization primitives available.


## OpenMP Multi-threading Part 2

Very often, when developing mutlti-threading software, we want and operation to be performed by one thread only or an operation should
be performed by a thread and when the performing thread finishes another thread can take over. These are operations that require
some sort of synchronization. We will will look into the following OpenMP constructs:

- ```omp master```
- ```omp single```
- ```omp masked```
- ```omp critical```

Let's start with ```omp master```

#### omp master

```omp master``` is one of the original OpenMP constructs and is very simple in intent—but easy to misuse if you don’t understand its synchronization behavior.
What ```omp master``` does:
- The enclosed block is executed only by the master thread
- The master thread is thread 0
- There is no implicit barrier at entry or exit
- Other threads skip the block and continue immediately

In other words, we can think of ```omp master``` as _Only thread 0 runs this, everyone else moves on._ Below is a C++ code snippet that
illustrates ```omp master```:

```
#include <omp.h>
#include <iostream>

int main()
{
    #pragma omp parallel num_threads(4)
    {
        int tid = omp_get_thread_num();

        #pragma omp master
        {
            std::cout << "Master section executed by thread "
                      << tid << "\n";
        }

        std::cout << "Thread " << tid << " continues\n";
    }
}

```

The important thing to notice is that there is no implict barrier at the end of the the construct. Having said this,
this construct is not appropriate to initialise data structures shared by all threads. ```omp single``` (see below) can be used
for this. In other words, this is not an sychronization construct but a construct that limits execution to the main thread. We can
turn it into a synchronization construct by placing an explicit barrier at the end as shown below

```
#pragma omp parallel
{
    #pragma omp master
    {
        initialize_shared_data();
    }

    #pragma omp barrier

    use_shared_data();  
}

```

Similarly avoid using ```omp task``` with this construct and prefer ```omp masked``` instead (see below). Although, it is legal to use
```omp task``` with ```omp master```, this can cause scheduling problems.

#### omp single

The construct ```omp single```  executes a block of code by exactly one thread in a parallel region. It is useful when we want to perform any of the following:

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
Below is an example using the construct

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

#### omp critical

```omp critical``` defines a mutual-exclusion region. In other words all threads get to execute the construct but one at the time.
The construct is useful for protecting shared data fom race conditions. Below is an example

```
#include <iostream>
#include <omp.h>

int main() {
    int counter = 0;

    #pragma omp parallel shared(counter)
    {
        #pragma omp critical
        {
            counter++;
        }
    }

    std::cout << "counter = " << counter << std::endl;
    return 0;
}

```

## Summary

This note builds on the introduction to OpenMP multi-threading by focusing on synchronization primitives used to control how and when threads execute shared code. 
It covers four key OpenMP constructs: ```omp master```, ```omp single```, ```omp masked```, and ```omp critical```.

- ```omp master```: Executes a code block only on the master thread (thread 0), with no implicit barrier. Other threads skip the block and continue immediately. Because of the lack of synchronization, it is not suitable for initializing shared data unless combined with an explicit ```omp barrier```. It should also be avoided for task creation due to potential scheduling issues.
- ```omp single```: Ensures a block of code is executed by exactly one thread, chosen at runtime. Unlike ```master```, it has an implicit barrier at the end, making it ideal for initialization, I/O, shared data setup, and task creation before other threads proceed.
- ```omp masked```: Introduced in OpenMP 5.0, it restricts execution to threads that satisfy a mask—by default, only the master thread. Like ```master```, it has no implicit barrier, but it is the preferred construct when combining with tasks, avoiding the scheduling pitfalls of ```master```.
- ```omp critical```: Defines a mutual-exclusion region where all threads may execute the code, but only one at a time. It is used to protect shared data from race conditions, though excessive use can harm performance.

Overall, the note clarifies that these constructs serve different purposes:

- ```omp master``` and ```omp masked``` limit which threads execute code,
- ```omp single``` both limits execution and synchronizes threads, and
- ```omp critical``` enforces safe, serialized access to shared resources.


## References
