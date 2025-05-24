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
