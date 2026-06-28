# qubit-note: Parallel Computing Series | OpenMP Part 7 | Example 1 Compute Mean & Variance

## Overview

In this qubit-note we will discuss a full OpenMP based example. The example, simply computes the mean and the variance
of a vector. The example is kept on purpose simple so that various deficiencies can be illustrated.

**keywords** openmp, c++, programing

## Example 1

In this example we will compute the mean and variance of a given vector. The mean is defined as

$$
\bar{x} = \frac{1}{N} \sum_{i=1}^N x_i
$$

The population variance is defined as 

$$
Var[x] = \frac{1}{N} \sum_{i=1}^N (x_i - \bar{x})^2
$$

----
**Remark**

There is also the sample variance which is defined as

$$
Var[x] = \frac{1}{N - 1} \sum_{i=1}^N (x_i - \bar{x})^2
$$

----

the snippet below is our implementation

```
#include <iostream>
#include <vector>
#include <cmath>

#include <omp.h>


namespace part7{


    double sum(const std::vector<double>& values){

        double sum_result = 0.0;
        const auto N = values.size();
        #pragma omp parallel for reduction(+:sum_result) shared(values)
            for (int i=0; i<N; ++i){
                sum_result += values[i];
            }
        

        return sum_result;
    }

    double mean(const std::vector<double>& values){
        auto sum_vals = sum(values);
        return sum_vals / values.size();
    }

    double variance(const std::vector<double>& values){
       
        
        const auto N = values.size();

        auto mean_val = mean(values);

        double sum_result = 0.0;
        #pragma omp parallel for reduction(+:sum_result) shared(values, mean_val)
            for (auto i=0; i<N; ++i){
                auto diff = values[i] - mean_val;
                sum_result += diff * diff;
            }
        

        return sum_result / values.size();
    }

}


int main(){

    omp_set_num_threads(4);
    using namespace part7;
    std::vector<double> data(10000, 1.0);

    auto mu = mean(data);
    auto var = variance(data);
    std::cout<<"mean: "<<mu<<" variance: "<<var<<std::endl;

    return 0;
}
```

Running the code you should see:

```
mean: 1 variance: 0
```

Let's discuss the code a bit. The code does two passes over the when we compute the variance. Performance-wise this may not be what we want.
For a large vector this two-pass approach may be problematic. Our code correctly, refactors the computation of the mean from computing the variance.
This is a sound sound engineering approach. However, as mentioned above following such an approach may be problematic. Thus, when designing for performance, sometimes
we need to deviate from some engineering principles like DRY. In addition, when designing for performance, we may have to change the
algorithms we use. Below, is a snippet of how we could compute the variance without passing over the data twice:


```
double variance(const std::vector<double>& values) {
    size_t N = values.size();

    double sum_val = 0.0;
    double sum_sq = 0.0;

    #pragma omp parallel for reduction(+:sum_val, sum_sq)
    for (size_t i = 0; i < N; ++i) {
        sum_val += values[i];
        sum_sq  += values[i] * values[i];
    }

    double mean = sum_val / N;
    return (sum_sq / N) - (mean * mean);
}
```


----
**Remark**

There are various algorithms for calculating the variance of a dataset.
Check the relevant wikipedia article: <a href="https://en.wikipedia.org/wiki/Algorithms_for_calculating_variance">Algorithms for calculating variance</a>
The parallel version of Welford's algorithm can also be used which in general would provide more stability at the cost of more complexity.

----


## Summary

This qubit-note presents a simple OpenMP-based C++ example that computes the mean and population variance of a vector in parallel using reduction clauses. It first implements a clean two-pass approach—one pass to compute the sum (and mean) and a second pass to compute the variance—highlighting good modular design but noting that multiple passes over large datasets can hurt performance. It then introduces a more efficient single-pass alternative that computes both the sum and sum of squares in one parallel loop and derives the variance from them, reducing memory traversal at the potential cost of numerical stability. The note emphasizes the trade-offs between software engineering principles, performance optimization, and numerical robustness in parallel algorithm design, mentioning that more stable methods like Welford’s algorithm can also be used.


## References