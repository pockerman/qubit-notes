# qubit-note: Parallel Computing Series | OpenMP Part 3 | Work Sharing

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

The program use two of the constructs we saw in - <a href="how_to/2026-01-15-OpenMP-Multi-threading-Part-2.md">qubit-note: Parallel Computing Series | OpenMP Multi-threading Part 2</a>
namely ```omp mster``` and ```omp single```. In this section we are interested in the ```omp for``` construct. So how work sharing is achieved in OpenMP ```omp for``` construct?





## Big picture

`#pragma omp for` achieves work sharing by:

1. Taking the **iteration space** of a loop
2. **Dividing it into chunks**
3. **Assigning chunks to threads** in the current parallel team
4. Enforcing **optional synchronization** at the end

All of this is done **by the OpenMP runtime**, not by you.

---

## Step-by-step: what happens at runtime

Given:

```cpp
#pragma omp parallel
{
    #pragma omp for
    for (int i = 0; i < 16; i++) {
        work(i);
    }
}
```

Assume **4 threads**.

---

### 1. Create the iteration space

OpenMP first defines the loop bounds:

```
i = 0 … 15
```

That’s **16 independent iterations**.

---

### 2. Choose a scheduling policy

If you don’t specify one:

```cpp
#pragma omp for
```

OpenMP uses:

```
schedule(static)
```

by default (unless overridden by `OMP_SCHEDULE`).

---

### 3. Partition iterations into chunks

For `schedule(static)`:

* Iterations are divided **contiguously**
* As evenly as possible

With 16 iterations, 4 threads:

```
Thread 0 → i = 0–3
Thread 1 → i = 4–7
Thread 2 → i = 8–11
Thread 3 → i = 12–15
```

Each thread knows *exactly* which iterations it owns.

---

### 4. Execute independently

Each thread runs:

```cpp
for (int i = my_start; i <= my_end; i++) {
    work(i);
}
```

No locks, no atomics — because iterations are assumed independent.

The loop index `i` is:

* **private**
* **unique per thread**

---

### 5. Synchronize (barrier)

At the end of the `omp for`:

* All threads **wait** at an implicit barrier
* Ensures all iterations are complete before moving on

Unless you say:

```cpp
#pragma omp for nowait
```

---

## Other scheduling strategies (how work is divided)

### `static` (default)

```cpp
#pragma omp for schedule(static)
```

* Divide once, at start
* Lowest overhead
* Best for uniform workloads

---

### `static, chunk`

```cpp
#pragma omp for schedule(static, 2)
```

Chunks of size 2:

```
Thread 0 → 0–1, 8–9
Thread 1 → 2–3, 10–11
Thread 2 → 4–5, 12–13
Thread 3 → 6–7, 14–15
```

(Cyclic distribution)

---

### `dynamic`

```cpp
#pragma omp for schedule(dynamic, 2)
```

* Threads request chunks **on the fly**
* Good for uneven workloads
* Higher overhead

---

### `guided`

```cpp
#pragma omp for schedule(guided)
```

* Large chunks first, smaller later
* Balance between static and dynamic

---

### `runtime`

```cpp
#pragma omp for schedule(runtime)
```

Defers decision to:

```
OMP_SCHEDULE=dynamic,4
```

---

## Why this works safely

OpenMP guarantees:

* Each iteration is executed **exactly once**
* No two threads get the same iteration
* Loop index is private
* Memory consistency at the barrier

🚫 If iterations depend on each other → **data race / wrong result**

---

## What OpenMP does *not* do

* It does **not** reorder iterations semantically
* It does **not** insert locks automatically
* It does **not** fix dependency bugs

You promise the loop is safe — OpenMP just schedules it.

---

## Mental model (very important)

Think of `omp for` as:

> “Take this loop, slice it up, hand slices to threads, then optionally wait.”

That’s it. Simple. Powerful.

---

If you want next, I can:

* show a timeline diagram for `static` vs `dynamic`
* explain false sharing & cache effects
* or walk through what happens in the OpenMP runtime internally

Just point the direction 👇




In order to ```omp for``` to work, our progam has to respect certain rules [1]:

- The loop index variable must be an integer
- The loop must have standard exist conditions 
- The loop index cannot be modified in the loop
- The loop iterations must be countable
- The loop must not have any loop-carried dependencies


## Summary

## References

1. Robert Robey, Yulian Zamora, _Parallel and High Perfromance Computing_, Manning Publications.