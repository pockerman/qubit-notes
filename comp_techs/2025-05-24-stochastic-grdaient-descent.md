# qubit-note: Stochastic Grdaient Descent

## Overview

In <a href="2025-05-17-gradient-descent.md">qubit-note: Gradient Descent</a> I introduced gradient descent as a simple
approach for finding minimum and maximum points of a function. I gave a simple example how to approximate
the parameters of a function using gradient descent. In this case, we need to load the whole data set into memory.
However sometimes this is not possible. One way to overcome this is to use 
<a href="https://en.wikipedia.org/wiki/Stochastic_gradient_descent">stochastic gradient descent</a> or SGD.


**keywords** stochastic-graident-descent, unconstrained-optimization, numerical-methods 

## Stochastic Grdaient Descent


Stochastic Gradient Descent is a variant of the standard Gradient Descent algorithm. 
Instead of computing the gradient of the loss function using the entire dataset (which is computationally expensive), 
SGD updates the model parameters using a single data point (or a small batch) at a time.

Here is a description how the algorithm works:

- Initialize model parameters randomly.
- Iterate over the dataset multiple times (epochs).
- For each training example (or mini-batch):

    1. Compute the gradient of the loss with respect to model parameters.
	2. Update parameters using the formula:

	$$\boldsymbol{\theta}_k = \boldsymbol{\theta}_{k-1} - \eta \nabla f|_{\boldsymbol{\theta}_{k-1}} $$


Stochastic gradinet descent updates the weights faster than GD or even batch gradient descent. It also introduces noise, which can help escape local minima.
However it may result is slower convergence as can be seen in the following figure

| ![gd-eta-01](./imgs/sgd_fluctuation.png)            |
|:---------------------------------------------------:|
|     **Figure 1. SGD fluctuation. Image from [1].**  |


This overshooting behavior, in general, complicates convergence to the exact minimum. However,  by slowly decreasing the learning rate $\eta$ it has been shown that SGD shows the same convergence behaviour as batch gradient descent and almost certainly converges to a local or the global minimum both for <a href="https://en.wikipedia.org/wiki/Convex_optimization">convex</a> and non-convex optimization problems. One other problem one may face with the SGD algorithm is that some bias may be introduced as the algorithm updates the weights on a per weights basis. This can be mitigated by suffling the data after each iteration.


SGD is often used with techniques like momentum, learning rate schedules, and mini-batching to improve performance. The following example
shows a Python code sample


```
import numpy as np
import matplotlib.pyplot as plt

# Generate some synthetic data
np.random.seed(42)
X = 2 * np.random.rand(100, 1)
true_w = 3.5
true_b = 1.2
y = true_w * X + true_b + np.random.randn(100, 1) * 0.5  # Add noise

# Initialize parameters
w = np.random.randn()
b = 0.0

# Hyperparameters
learning_rate = 0.01
epochs = 20

# SGD training
for epoch in range(epochs):
    for i in range(len(X)):
        xi = X[i]
        yi = y[i]

        # Prediction
        y_pred = w * xi + b

        # Compute gradients
        error = y_pred - yi
        dw = 2 * xi * error
        db = 2 * error

        # Update weights
        w -= learning_rate * dw
        b -= learning_rate * db

    
# Plotting
plt.scatter(X, y, color='blue', label='Data')
plt.plot(X, w * X + b, color='red', label='Fitted Line')
plt.legend()
plt.title("SGD Linear Regression")
plt.xlabel("X")
plt.ylabel("y")
plt.show()

```

Running the script produces the following plot:



| ![gd-eta-01](./imgs/sgd_linear_regression.png)   |
|:------------------------------------------------:|
|     **Figure 2. Linear regression with SGD.**    |

## References

1. <a href="https://ruder.io/optimizing-gradient-descent/">An overview of gradient descent optimization algorithms</a>