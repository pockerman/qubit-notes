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