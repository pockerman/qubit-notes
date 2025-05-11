import random

def f(x):
    """Function to integrate."""
    return x ** 2

def monte_carlo_integration(f, a, b, num_samples=100000):
    total = 0.0
    for _ in range(num_samples):
        x = random.uniform(a, b)
        total += f(x)
    estimate = (b - a) * total / num_samples
    return estimate

# Integration bounds
a = 0
b = 1

# Perform integration
estimated_integral = monte_carlo_integration(f, a, b)
print(f"Estimated integral of f(x) = x^2 over [{a}, {b}] is: {estimated_integral:.5f}")

