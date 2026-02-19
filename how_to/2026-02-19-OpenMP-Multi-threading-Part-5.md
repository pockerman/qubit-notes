# qubit-note: Parallel Computing Series | OpenMP Part 5 | Variable Scope

## Overview

This is part 5 in the OpenMP programming series and we will look into variable scope.
This is very important in order to convert an application to high-level OpenMP.
In a nutshell, the variable scope determines whether a variable is:

- Shared: One memory location, visible to all threads
- Private: Each thread has its own copy



## Variable scope

In OpenMP, multiple threads execute code in parallel. In order to avoid undefined behaviour we need to understand how threads view
the various variables in a program. In OpenMP, we have two types of scopes:

- Shared: One memory location, visible to all threads
- Private: Each thread has its own copy


As a rule of thumb, a variable that is placed on the stack is considered private i.e. private to the thread and those
placed in the heap are shared [1]. Private variables are undefined at entry and after the exit of a parallel region. In some cases, we can use
```firstprivate``` and ```lastprivate``` clauses to modify this behavior.


Let's discuss some scoping rules.

### Default scoping rules

The following type of variables are shared by default inside a ```#pragma omp parallel``` :

- Variables declared outside the paralle region
- Global and static variables
- Heap-allocated variables

For these variables all threads will see the same memory location.

The following variables are private by default:

- Loop index variables in ```#pragma omp for```
- Variables declared inside the parallel block

Each thread gets its own independent copy.

OpenMP allows us to explicitly set the scope of variable using various clauses

### Explicit Scoping Clauses

OpenMP lets you control scoping explicitly.

####  `shared(variable)`

All threads access the same variable.

```c
#pragma omp parallel shared(x)
```

Use when:

- Threads need to read or update common data
- Combined with synchronization (e.g., `atomic`, `critical`)



#### `private(variable)`

Each thread gets its own uninitialized copy.

```c
#pragma omp parallel private(x)
```

Important:

- The private copy is **not initialized**
- Original value is not preserved



#### `firstprivate(variable)`

Each thread gets its own copy initialized with the original value.

```c
#pragma omp parallel firstprivate(x)
```

Use when:

- Threads need a starting value from the original variable


#### `lastprivate(variable)`

Used with work-sharing constructs (`for`, `sections`).

The variable gets the value from the **last iteration** executed.

```c
#pragma omp for lastprivate(x)
```


#### `reduction(op:variable)`

Each thread gets a private copy.
At the end, values are combined using an operation.

```c
#pragma omp parallel for reduction(+:sum)
```

Common operations:

* `+`
* `*`
* `min`
* `max`
* `&`, `|`, `^`


#### `default` clause 

You can force explicit scoping and this a highly recommended practice :

```c
#pragma omp parallel default(none)
```

This requires you to declare every variable as:

* `shared`
* `private`
* `firstprivate`
* etc.

This prevents accidental race conditions and is considered best practice.

Below is summary table of these rules.



| Clause          | Shared? | Initialized?   | Notes                      |
| --------------- | ------- | -------------- | -------------------------- |
| default(shared) | Yes     | Yes            | Outside vars               |
| private         | No      | No             | New copy per thread        |
| firstprivate    | No      | Yes            | Copy initialized           |
| lastprivate     | No      | Yes (final)    | Gets last iteration value  |
| reduction       | No      | Yes (combined) | Safe parallel accumulation |



## Summary

This part of the OpenMP series explains variable scoping, which determines how variables are seen by threads in a parallel region and is crucial for avoiding race conditions and undefined behavior. In OpenMP, variables are either shared (one memory location visible to all threads) or private (each thread has its own copy). By default, variables declared outside a `parallel` region, as well as global, static, and heap-allocated variables, are shared, while loop indices and variables declared inside the parallel block are private. Private variables are uninitialized upon entry and exit unless modified using clauses like `firstprivate` (initialized copy) or `lastprivate` (keeps the final iteration’s value). OpenMP also provides explicit scoping clauses such as `shared`, `private`, `firstprivate`, `lastprivate`, and `reduction` (for safe parallel accumulation), and recommends using `default(none)` to force explicit scope declarations and prevent accidental race conditions.


## References

1. Robert Robey, Yulian Zamora, _Parallel and High Perfromance Computing_, Manning Publications.
