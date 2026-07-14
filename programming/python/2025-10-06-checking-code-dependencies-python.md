# qubit-note: Checking Code Dependencies in Python Codebases

## Overview

As software sustems evolve, the codebase they rely on tends to disintegrate and if action is not excercised,
if will trun into a big ball of mud. This is something we defnitely don't want to happen as working in such codebases
is exceedingly difficult. There are a few actions that software architects can impose on software developers in order
to prevent this from happening. One of these actions is to analyze the dependencies in a project.

In this quibit note, I will discuss how to examine the dependnecies of a Python codebase.

**keywords** codebase-review, python, architecture-review

## Checking code dependencies on Python codebases

Python has a number of tools for managing dependencies. Some of the most popular at the time of writing are <a href="https://pypi.org/project/pip/">pip</a> and <a href="https://github.com/astral-sh/uv">uv</a>. In this note we will assume that our project is managed via ```pip```.


Listing the installed packages in a Python enviroment is easy:

```
pip freeze > reqs.txt
```

This outputs the installed packages saved in  ```reqs.txt```. However, we are interested in finding what libraries your code actually imports:

```
pip install pipreqs
pipreqs /path/to/your/project

```

It outputs a ```requirements.txt``` with only the libraries that appear in your code. You can compare it with your pip freeze output to detect unused dependencies.

If you want to generate a graph of imports you can use <a href="https://furius.ca/snakefood/">snakefood</a> however this package is not supported anymore.  You may want to use <a href="https://pypi.org/project/pipdeptree/">pipdeptree</a>:

```
pip install pipdeptree
pipdeptree

``` 

<a href="https://github.com/seddonym/import-linter">import-linter</a> allows you to enforce import rules and check architectural boundaries:

```
pip install import-linter
lint-imports
```

Checking for outdate packages:

```
pip list --outdated

```

 Vulnerability audits we can be executed:

 ```
pip install safety
safety check

 ```

 This checks your dependencies against known CVE databases.

 Finally, cehcking for missing dependencies:

 ```
 pip check
 ```

## Summary

In this qubite-note I went over a number of Python tools we can use in order to validate in many different apects the quality of a codebase.
These tools can be integrated into a CI/CD pipeline in order to automatically safeguard out codebase.


## References

1. <a href="https://pypi.org/project/pip/">pip</a>
2. <a href="https://github.com/astral-sh/uv">uv</a>
3. <a href="https://furius.ca/snakefood/">snakefood</a>
4. <a href="https://pypi.org/project/pipdeptree/">pipdeptree</a>
5. <a href="https://github.com/seddonym/import-linter">import-linter</a>
