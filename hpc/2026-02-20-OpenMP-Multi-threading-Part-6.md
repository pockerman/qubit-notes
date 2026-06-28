# qubit-note: Parallel Computing Series | OpenMP Part 6 | Function-level Parallelization

## Overview

We have seen how to create parallel regions and how to parallelize for loops with OpenMP. We also discussed variable scopes in OpenMP.
Functions are a cornerstone of software engineering and thus, in this qubit-note, we will discuss how to use OpenMP constructs within functions

**keywords** openmp, function-level-parallelization, c++, programming

## Function-level parallelization


Once we convert a function to an OpenMP parallel region, the standard provides far less control over the thread scope of the variables [1].
However, the defaults for variable scope in functions most of the time work well. Recall that in a avriable declared in function is allocated on the stack
and thus has a private scope by default. If the variable should be shared we can either declare it as ```static``` or
declare it a file scope.

Here is an example

```

// the pointer to y is private
void my_func(double* y){

	// pointer to x is private
	double *x;

	// pointer to x1 is shared
	static double *z;

#pragma omp parallel default(none) private(x) shared(z){

	// memory for both x and z is shared
	if(omp_get_thread_num() == ){
		x = new double;
		z = new double;
	}
}

}
```

The memory for the ```x``` variable is on the heap and thus shared but the pointer is private so essentially the memory is only accessible from thread zero.
In contrast, ```z``` has both memory and pointer shared amongst all threads.


## Summary

This qubit-note introduces the idea of using OpenMP constructs inside functions to achieve function-level parallelization in C++. It explains how variable scope behaves in this context, emphasizing that local (automatic) variables declared inside a function are private by default, while `static` or file-scope variables are shared among threads. Through a pointer-based example, the note attempts to distinguish between the scope of a pointer variable and the memory it references, highlighting that heap-allocated memory is shared in a shared-memory model, but access to it depends on whether the pointer itself is private or shared.



## References

1. Robert Robey, Yulian Zamora, _Parallel and High Perfromance Computing_, Manning Publications.