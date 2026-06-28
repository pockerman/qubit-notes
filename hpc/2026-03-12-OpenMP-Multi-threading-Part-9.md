# qubit-note: Parallel Computing Series | OpenMP  Part 9 | Task Parallelism with OpenMP 1

## Overview

In this note we will discuss how to do task parallelism with OpenMP.


## Task Parallelism with OpenMP 1

Task parallelism in OpenMP lets you run independent pieces of work (tasks) concurrently instead of splitting a loop iteration space among threads. It’s ideal when:

- Work units are irregular or recursive
- Tasks are created dynamically
- Execution order isn’t strictly sequential

Typical examples inclide: tree traversal, divide-and-conquer algorithms (quicksort, mergesort), pipelines, or asynchronous workloads.

In OpenMP, we create tasks using the _task_ clause:

```
#pragma omp task
```
A thread generates tasks, and OpenMP schedules them across available threads. Here is the basic pattern:

```
#pragma omp parallel
{
    #pragma omp single
    {
        // create tasks here
    }
}
```

Here is an example:

```
#include <stdio.h>
#include <omp.h>

int main() {
    #pragma omp parallel
    {
        #pragma omp single
        {
            for(int i = 0; i < 5; i++) {
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

Frequently, we may want to wait for tasks to finish, we can do this using th _taskwait_ clause:

```
#pragma omp parallel
{
    #pragma omp single
    {
        #pragma omp task
        work1();

        #pragma omp task
        work2();

        #pragma omp taskwait
        printf("Both tasks finished\n");
    }
}
```

Variables in tasks follow OpenMP data-sharing rules. Recall some common clauses:

- ```shared(var)```: shared across threads
- ```private(var)```: each task gets its own copy
- ```firstprivate(var)```: copy initialized with original value

OpenMP can enforce ordering using dependencies.

```
#pragma omp task depend(out:A)
produce(A);

#pragma omp task depend(in:A)
consume(A);
```

Some rule of thumbs of when to use tasks are:

- Work size is unpredictable
- Recursive algorithms
- Graph/tree traversal
- Producer-consumer pipelines

From a performance perspective, we should avoid creating too many tiny tasks.

Use loop paralleliszation when:

- Iterations are uniform
- Workload is predictable

```
#pragma omp parallel
{
    #pragma omp single
    {
        #pragma omp taskloop
        for(int i=0;i<n;i++)
            process(i);
    }
}
```

## Summary

Task parallelism in OpenMP allows a program to execute independent units of work, called tasks, concurrently instead of dividing loop iterations among threads. Tasks are created using `#pragma omp task`, typically inside a `parallel` region with a `single` directive so that one thread generates tasks while the runtime distributes them across available threads. This approach is well suited for irregular or dynamic workloads such as recursive algorithms, tree or graph traversals, divide-and-conquer methods like quicksort or mergesort, and pipeline-style computations. Synchronization between tasks can be controlled using `#pragma omp taskwait`, while variable access is managed with data-sharing clauses such as `shared`, `private`, and `firstprivate`. OpenMP can also enforce execution order using task dependencies with `depend(in/out)`. In practice, task parallelism is most effective when workloads are unpredictable, while traditional loop parallelization (e.g., `taskloop` or `parallel for`) is preferred for regular, evenly distributed computations, and developers should avoid creating too many very small tasks for performance reasons.


## References

