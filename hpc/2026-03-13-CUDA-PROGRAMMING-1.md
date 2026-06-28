# qubit-note: CUDA Programming Part 1 | Hello World

## Overview


Kernels are fundamental to CUDA because
they enable the GPU to process large amounts of data simultaneously, leveraging its parallel
processing capabilities.
Kernels operate within a hierarchical structure of threads, blocks, and grids. A thread is the
smallest unit of execution in CUDA, and multiple threads are grouped together into blocks. Each
block runs independently and can be scheduled on any of the GPU’s processing units.

As we can see in Figure 3.1, blocks are organized into grids. The grid is the overall structure that
contains all the blocks and represents the entire workload to be executed by the kernel. When we
launch a kernel, we need to specify the number of blocks in the grid and the number of threads
in each block.

```
#include <iostream>
#include <cuda_runtime.h>

// GPU kernel
__global__ void helloFromGPU() {
    printf("Hello World from GPU thread %d!\n", threadIdx.x);
}

int main() {
    std::cout << "Hello World from CPU!" << std::endl;

    // Launch kernel with 1 block and 5 threads
    helloFromGPU<<<1, 5>>>();

    // Wait for GPU to finish before exiting
    cudaDeviceSynchronize();

    return 0;
}
```

## Summary

## References

