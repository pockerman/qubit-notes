# qubit-note: Monte Carlo Integration

## Overview

Frequently in applications we need to evaluate integrals for which there is no analytical solution.
Numerical methods allow as to overcome this by estimating the integrals in specific points.
<a href="https://en.wikipedia.org/wiki/Monte_Carlo_integration">Monte Carlo integration</a> is just one of these methods. 
Monte Carlo integration works due to the <a href="https://en.wikipedia.org/wiki/Law_of_large_numbers">law of large numbers</a>
and it becomes really effective as the dimensionality of the integral grows.

**keywords** numerical-methods, integration, Monte-Carlo-methods


## Monte Carlo intergration

Let's assume that we want to evaluate the integral

$$I=\int_a^b h(x) dx$$

If $f$ is a polynomial or a trigonometric function, then this integral can be calculated in closed form. 
However, in many cases there may not be  a closed for solution for $I$. 
Numerical techniques, such as <a href="https://en.wikipedia.org/wiki/Gaussian_quadrature">Gaussian quadrature</a> 
or the <a href="https://en.wikipedia.org/wiki/Trapezoidal_rule">trapezoid rule</a> can  be 
employed in order to evaluate $I$. Monte Carlo integration is yet another techinque for evaluating complex integrals that is
notable for its simplicity and generality [4].

Let's begine by rewriting $I$ as follows

$$I=\int_a^b \omega(x)f(x) dx$$

where $\omega=h(x)(b-a)$ and $f(x) = 1/(b-a)$ i.e. $f$ is the probability density for a uniform random variable over $(a,b)$ [4]. 
Recall that the expectation for a continuous variable $X$ is given by

$$E\left[X\right]=\int xf(x)dx$$

Hence, 

$$I=E\left[\omega(X)\right]$$

This is the basic Monte Carlo integration method [4]. In order to evaluate the integral $I$, we evaluate the following expression

$$\hat{I} = \frac{1}{n}\sum_{i=1}^{N}\omega(x_i)$$

where $x \sim U(a,b)$. By the 
<a href="https://en.wikipedia.org/wiki/Law_of_large_numbers">law of large numbers</a> it follows, see [4],

$$\hat{I}\rightarrow E\left[\omega(X)\right] = I$$

Notice that the law of large numbers provides us with probability convergence. 
Hence $\hat{I}$ will <a href="https://en.wikipedia.org/wiki/Convergence_of_random_variables">converge in probability</a> to $I$. 
The standard error, $\hat{se}$, for the estimate is, see [4]:

$$\hat{se} = \frac{s}{\sqrt{n}}$$

where

$$s^2  = \frac{\sum_{i}^{N}(\omega(x_i) - \hat{I} )^2}{n - 1}$$

Moreover, a $1-\alpha$ confidence interval for the estimate is given from, see [4], 

$$\hat{I} \pm z_{\alpha/2}\hat{se}$$

The following Python script demonstrates a basic example of Monte Carlo integration.

```
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

```

Running the code above produces the following output

```
Estimated integral of f(x) = x^2 over [0, 1] is: 0.33412
```


## References

1. <a href="https://en.wikipedia.org/wiki/Monte_Carlo_integration">Monte Carlo integration</a> 
2. <a href="https://en.wikipedia.org/wiki/Law_of_large_numbers">Law of large numbers</a>
3. <a href="https://en.wikipedia.org/wiki/Gaussian_quadrature">Gaussian quadrature</a>
4. Larry Wasserman, _All of Statistics. A Concise Course in Statistical Inference_, Springer 2003.
5. <a href="https://en.wikipedia.org/wiki/Convergence_of_random_variables">Convergence of random variables</a> 
