# Note: Task-based Parallelism With Ray Part 1


## Overview

When working with parallel programs two patterns frequently arise; <a href="https://en.wikipedia.org/wiki/Data_parallelism">data parallelism</a>
and <a href="https://en.wikipedia.org/wiki/Task_parallelism">task parallelism</a>.

In this note I discuss how to implement task-based parallelism using <a href="https://www.ray.io/">Ray</a>.


**keywords:** Ray, Python, task-parallelism, distributed-systems

## Task-based parallelism with Ray

Data and task parallelism are two computing patterns that frequently arise when working with parallel and/or
distributed software.

One of the most common applications of the former pattern is to apply the same operation(s) on all the available data.
For example calculate the sum of all the elements in an array; in this case, we distribute non-overlapping
data chuncks to the available processing elements and then collect these results for a final reduction operation
in order to compute the final result. If you have ever worked with simulating fluid flows this is a typical workflow.

In contrast, when doing task parallelism each processing element performs a different operation on the possibly 
same data. For example consider an application that accepts an image with the aim to classify it.
The application requirements are simple:

- Get user image
- Email user that you have his image
- Classify image
- Email user user with the classification result

These are different tasks that to an extend can be performed independnetly although some synchronization is required.
<a href="https://patterns.eecs.berkeley.edu/?page_id=609">Task graphs</a> can be used in order to organise task-based parallelism.

In this note I won't go into these details but rather simply go over the API that Ray exposes for task-based parallelism.

### Expressing task parallelism with Ray

Two of the core components of Ray are <a href="https://docs.ray.io/en/latest/ray-core/tasks.html">Tasks</a> and 
<a href="#">Actors</a>. A task is simply an arbitrary function that can be executed asynchronously by a processing element e.g. a CPU.
Here is an example:

```
import ray
from ray import ObjectRef
import time


@ray.remote
def remote_task_1(data: int) -> int:
    return data + 1

@ray.remote
def remote_task_2(data: float) -> float:
	time.sleep(10)
	return data * 2.0


@ray.remote
def remote_task_3(data: int) -> float:

	# this task cannot proceed
	# if task2 is not ready
	result_task_2 = ray.get(remote_task_2.remote(2.0))
	return data + result_task_2


if __name__ == '__main__':

	# initialize the Ray cluster
	ray.init()

	# Invoke this remote function, use the `remote` method.
	# this is an asynchronous op
	obj_ref_1 = remote_task_1.remote(2)
	

	# do work locally
	counter = 0
	for _ in range(10):
		counter += 1

	# get the result from the first task
	# this blocks if the result is not ready
	result_task_1 = ray.get(obj_ref_1)

	# add this to the counter
	counter += result_task_1


	
	final_answer_ref = remote_task_3.remote(counter)
	final_answer = ray.get(final_answer_ref)
	print(f'Final answer is {final_answer}')
	ray.shutdown()

```

In the example above, the _main_ driver acts like a coordinator between the tasks. 
The decorator ```ray.remote``` comes with several options in order to customize how a task will be computed.
For more information, checkout the official documentation: <a href="https://docs.ray.io/en/latest/ray-core/api/doc/ray.remote.html#ray.remote">ray.remote</a>.



## References

1. <a href="https://en.wikipedia.org/wiki/Data_parallelism">Data parallelism</a>
2. <a href="https://en.wikipedia.org/wiki/Task_parallelism">Task parallelism</a>
3. <a href="https://www.ray.io/">Ray</a>
4. <a href="https://patterns.eecs.berkeley.edu/?page_id=609">Task graphs</a>
