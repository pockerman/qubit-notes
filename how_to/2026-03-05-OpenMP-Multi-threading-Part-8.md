# qubit-note: Parallel Computing Series | OpenMP Part 8 | Example 2 Compute Mean Usin smid

## Overview

<a href="2026-02-26-OpenMP-Multi-threading-Part-7.md">Example 1 Compute Mean & Variance</a> showed a basic implementation of computing the mean and variance of a vector
using OpenMP. In this example, we will see how to use vecorisation with OpenMP. It turns out that this is fairly easy; just add the ```simd``` clause in the
parallel for clause.

**keywords** openmp, vectorisation, c++, programing

## Example 2

This example implements again the calculation of the mean value of a vector from <a href="2026-02-26-OpenMP-Multi-threading-Part-7.md">Example 1 Compute Mean & Variance</a>
by using vectorisation. The ```simd``` clause instructs the compiler to vectorize a loop; i.e. execute multiple iterations simultaneously 
using SIMD instructions (Single Instruction, Multiple Data) like AVX or SSE.

----
**Remark**

On a linux machine, you can check which vectorisation ops the CPU supports by using

```
grep -m1 flags /proc/cpuinfo
```
----

Below is the slightly altered code from Example 1 that uses the simd clause.

```
double sum(const std::vector<double>& values){

        double sum_result = 0.0;
        const auto N = values.size();
        #pragma omp parallel for simd reduction(+:sum_result) shared(values)
            for (int i=0; i<N; ++i){
                sum_result += values[i];
            }
        

        return sum_result;
    }
```


Here are some common clauses used together with simd:

```
#pragma omp simd aligned(a,b:32)
#pragma omp simd reduction(+:sum)
#pragma omp simd private(tmp)
#pragma omp simd safelen(8)
```

## Summary

This is it for this note. In summary, OpenMP makes it very easy to exploit vectorisation instructions by using the ```simd``` clause.

## References