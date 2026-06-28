# qubit-note: Asynchronous Programming C++ | Promises and Futures

## Overview

In this note we will looke into promises and futures in C++. These are twi ways to
return values from ```std::thread``` execution. A lot of the material in this  note are taken from [1].
Futures and prompises are essential blocks when discussing asynchronous programming in C++.


## Asynchronous Programming C++ | Promises and Futures

A future is an object that represents some undetermined result that will be completed sometime in
the future. A promise is the provider of that result.

The ```std::promise``` and ```std::future``` pair implements a one-shot producer-consumer channel
with the promise as the producer and the future as the consumer. The consumer (std::future)
can block until the result of the producer (std::promise) is available.

The basic principle behind achieving asynchronous execution using promises and futures is that a
function we want to run to generate a result is executed in the background, using a new thread or
the current one, and a future object is used by the initial thread to retrieve the result computed by
the function. This result value will be stored when the function finishes, so meanwhile, the future
will be used as a placeholder. The asynchronous function will use a promise object to store the result
in the future with no need for explicit synchronization mechanisms between the initial thread and
the background one. When the value is needed by the initial thread, it will be retrieved from the
future object. If the value is still not ready, the initial thread execution will be blocked until the future
becomes ready. So result communication
and synchronization between threads is managed by the promise-future pair.

Also, promises can communicate if an exception was raised instead of returning a valid value and,
they will make sure that its lifetime persists until the thread finishes and writes the result to it.
Therefore, a promise is a facility to store a result (a value or an exception) that is later acquired
asynchronously via a future. A promise object is only intended to be used once and cannot be
modified afterward.
Apart from a result, each promise also holds a shared state. The shared state is a memory area that
stores the completion status, synchronization mechanisms, and a pointer to the result. It ensures
proper communication and synchronization between a promise and a future by enabling the promise
to store either a result or an exception, signal when it’s complete, and allowing the future to access
the result, blocking if the promise is not yet ready. The promise can update its shared state using the
following operations:


### Futures

Futures are defined in the ```<future>``` header file as ```std::future```.
As we saw earlier, a future is the consumer side of the communication channel. It provides access to
the result stored by the promise.
A std::future object can be created in three different ways:

1. From a ```std::promise``` object by calling ```get_future()```
2. Through a ```std::packaged_task``` object 
3. A call to the ```std::async``` function

Like promises, futures can be moved but not copied for the same reasons. To reference the same shared
state from multiple futures, we need to use shared futures (explained in the next section, Shared futures).
The get() method can be used to retrieve the result. If the shared state is still not ready, this call will
block by internally calling wait(). When the shared state becomes ready, the result value is returned.
If an exception was stored in the shared state, that exception will be rethrown:


```std::future``` also provides functions to block the thread and wait for a result to be available. These
functions are:
- ```wait()``` 
- ```wait_for()``` 
- ```wait_until()```

The ```wait()``` function will block indefinitely until the result is ready, ```wait_for()``` for a period, and ```wait_until()``` until a specific time has been reached. All will return as soon as the result is available within those waiting periods.


## Summary


## References

1. Javier Reguera-Salgado and Juan Antonio Rufes, _Asynchronous Programming with C++_, 1st Edition, Pack Publications.