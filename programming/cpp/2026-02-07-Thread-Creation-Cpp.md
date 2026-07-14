# qubit-note: Programming | Thread Creation in C++

The main library to create and manage threads in C++ is the thread library. First, let’s go through a
recap about threads. Then we will dive into what the thread library offers.


In C++, threads allow multiple functions to run concurrently. The thread class defines a type-safe
interface to a native thread. This class is defined in the std::thread library, in the <thread>
header file in the Standard Template Library (STL). It is available from C++11 onward.

Thread creation
When a thread is created, it executes immediately. It is only delayed by the OS scheduling process. If
there are not enough resources to run both parent and child threads in parallel, the order in which
they will run is not defined

The constructor argument defines the function or function object to be executed by the thread.
This callable object should not return anything, as its return value will be ignored. If for some reason
the thread execution ends with an exception, std::terminate is called unless an exception is
caught, as we will see later in this chapter.6