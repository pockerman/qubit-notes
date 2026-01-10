# qubit-note: Parallel Computing Series | OpenMP Multi-threading Part 1

## Overview

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

## Summary

## References