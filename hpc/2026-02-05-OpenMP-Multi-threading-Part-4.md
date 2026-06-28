# qubit-note: Parallel Computing Series | OpenMP Part 4 | Reduction Operations

## Overview

<a href="how_to/2026-01-29-OpenMP-Multi-threading-Part-3.md">qubit-note: Parallel Computing Series | OpenMP Part 3 | Parallelization of for Constructs</a>
discussed how to parallelize for loops with OpenMP. This is an example of work sharing. Another example related to work sharing is reduction operations.
An example of a reduction operation is to  calculate the sum of the elements of an array in parallel. OpenMP can easily handle such operation.

**keywords** openmp, reduction-operations, c++, programing

## Reduction operations

A reduction operation lets multiple threads safely combine their partial results into one final value.
Think of problems like:

- summing numbers
- finding a max/min
- counting items
- combining values with logical or bitwise ops

Without reduction, you’d get race conditions because multiple threads would try to update the same variable at the same time.
With OpenMP, each thread:

1. Gets its own private copy of a variable
2. Updates that copy independently
3. At the end of the parallel region, OpenMP combines all the copies using the specified operator

Below is the basic syntax

```cpp
#pragma omp parallel for reduction(operator : variable)
```

Some of the operators supported are:


- `+` addition
- `*` multiplication
- `-` subtraction (careful: order matters)
- `max`, `min`
- `&&`, `||`
- `&`, `|`, `^`

Below is an example summing the elements of an array



```cpp
#include <omp.h>
#include <iostream>

int main() {
    const int N = 1000;
    int sum = 0;

    #pragma omp parallel for reduction(+:sum)
    for (int i = 0; i < N; i++) {
        sum += i;
    }

    std::cout << "Sum = " << sum << std::endl;
    return 0;
}
```

The following example compute the maximum value of an array


```cpp
int maxVal = INT_MIN;

#pragma omp parallel for reduction(max:maxVal)
for (int i = 0; i < N; i++) {
    if (arr[i] > maxVal)
        maxVal = arr[i];
}
```

Note that the shared variable has to be initialised before the parallel region.
OpenMP also allows us to perform multiple reduction operations as shown below.


```cpp
int sum = 0;
int maxVal = INT_MIN;

#pragma omp parallel for reduction(+:sum) reduction(max:maxVal)
for (int i = 0; i < N; i++) {
    sum += arr[i];
    if (arr[i] > maxVal)
        maxVal = arr[i];
}
```

In this case, each reduction is handled independently.
Some common problems when using reductions are:

- Forgetting `reduction` this will lead to race condition
- Using non-associative ops (like floating-point `-`)
- Expecting deterministic floating-point results
- Modifying reduced variable outside the reduction context


## Summary

This qubit note explains reduction operations in OpenMP as part of the broader topic of work sharing, following the parallelization of `for` loops. Reduction is used when multiple threads need to combine partial results into a single final value safely.

A reduction works by giving each thread a private copy of a shared variable, letting threads update their copies independently, and then combining all copies at the end of the parallel region using a specified operator. This avoids race conditions that would occur if threads updated the same variable directly.

The note introduces the basic OpenMP syntax:

```cpp
#pragma omp parallel for reduction(operator : variable)
```

Common use cases include sums, products, min/max values, counters, and logical or bitwise combinations. Supported operators include `+`, `*`, `-`, `max`, `min`, logical (`&&`, `||`), and bitwise (`&`, `|`, `^`).

Examples show how to:

- Compute the sum of array elements in parallel
- Find the maximum value in an array
- Perform multiple reductions simultaneously (e.g., sum and max)

A key requirement is that the reduced variable must be initialized before entering the parallel region. Each reduction is handled independently by OpenMP.

The note concludes by highlighting common pitfalls, such as forgetting to use `reduction`, using non-associative operations (especially with floating-point values), expecting deterministic floating-point results, and modifying reduced variables outside the reduction context.


## References

1. Robert Robey, Yulian Zamora, _Parallel and High Perfromance Computing_, Manning Publications.