# qubit-note: Coroutine Chaining & Asynchronous Queues in Python

## Overview

Libraries such as <a href="https://fastapi.tiangolo.com/">FastAPI</a> utilize ```asyncio``` for delivering high performnca web frameworks.
In addition, asynchronous programming is a programming paradigm that is very well suited for I/O bound tasks. 

In this qubit note, I want to dsicuss two core patterns that frquently arise when employing asynchronous programming namely;
coroutine chaining and asynchronous queues. This note is essentially taken from the article <a href="https://realpython.com/async-io-python/#conclusion">Python's asyncio: A Hands-On Walkthrough</a>

**keywords** Asynchronous-programming, Python, High-Performance-Computing, asyncio

## Coroutine chaining & asynchronous queues

At the core of ```asyncio``` is the coroutine concept. Without getting into  much technical details, a coroutine function
can pause its execution and revoked again when needed. We can define one using the ```async``` keyword:

```
async def my_coro() -> None:
	# do somthing
```

In order to get a result back or apply the effects of a coroutine, we need to ```await``` for it:

```
async def add(a, b) -> int:
	return a + b

sum = await add(1, 2)	
```

Given that a coroutine is awaitable, it means that we can chain coroutines together i.e. awaiting one coroutine and passing its result into the next [2]. Within a  coroutine chain, each step depends on the previous one. Here is a toy example:

```
async def task_1(arg) -> SomeResult:
	return SomeResult(arg)

async def task_2(arg) -> SomeOtherResult:
	return SomeOtherResult(arg)

async def process_input(args):
	some_result = await task_1(args)
	some_other_result = await task_2(some_result)	
```

###  Asynchronous queues

Queues are one of the approaches that we can create asynchrounous workflows in a system. The consure-producer pattern
is a common computational pattern in these scenarios. The ```asyncio``` library provides support for asynchronous queues.
Here is minimalistic example:

```
import asyncio
import random

async def producer(queue, n):
    for i in range(n):
        # Simulate producing an item
        await asyncio.sleep(random.uniform(0.1, 0.5))
        item = f"item-{i}"
        await queue.put(item)
        print(f"Produced: {item}")
    # Signal that production is done
    await queue.put(None)

async def consumer(queue):
    while True:
        item = await queue.get()
        if item is None:
            break  # End of production
        print(f"Consumed: {item}")
        # Simulate processing time
        await asyncio.sleep(random.uniform(0.2, 0.6))

async def main():
    queue = asyncio.Queue()
    producer_task = asyncio.create_task(producer(queue, 5))
    consumer_task = asyncio.create_task(consumer(queue))

    await asyncio.gather(producer_task, consumer_task)

if __name__ == "__main__":
    asyncio.run(main())

```


## Summary

In this  note I discussed two  key asynchronous programming patterns in Python using ```asyncio```; coroutine chaining and asynchronous queues. It explains how coroutines, defined with the ```async``` keyword, can pause execution and resume later, allowing them to be chained together where each step awaits the result of the previous one. Additionally, it highlights the producer-consumer pattern implemented with asynchronous queues, enabling efficient I/O-bound workflows, as commonly used in high-performance web frameworks like FastAPI. An example demonstrates how producers and consumers interact using ```asyncio.Queue``` to manage tasks concurrently

## References

1. <a href="https://fastapi.tiangolo.com/">FastAPI</a> 
2. <a href="https://realpython.com/async-io-python/#conclusion">Python's asyncio: A Hands-On Walkthrough</a>