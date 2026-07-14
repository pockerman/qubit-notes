# qubit-note: Unit testing with ```pytest```

The importance of software testing has been well appreciated. As the systems we develop become more complex, e.g.
introding machine learning pipelines and models, testing is becoming even more important. In this post, we will go
over  Python's ```pytest``` package. 
Let's dive in. 

## Unit testing with ```pytest```

Let's first try to install ```pytest```. This is easilly done using ```pip```

```bash
pip install pytest
```

Let's consider the following function in the ```str_utils.py``` module

```python

def add_strs(str1: str, str2: str) -> str:
	if len(str1) != len(str2):
		raise ValueError(f"Invalid lengths. {len(str1)} != {len(str1)}2)
		
	return str1 + "_" + str2

```


When using ```unittest``` in order to test the function above, we need to create a class that inherits from ```unittest.TestCase```.
With ```pytest``` we can has something as simple as

```python

from str_utils import add_strs

def test_add_strs() -> None:
	str1 = "Hello"
	str2 = "World"
	
	result = add_strs(str1. str2)
	assert result == str1 + "_" + str2
```
Save this function in a file called ```test_str_utils.py```
We can then run this test using

```bash
pytest test_str_utils.py
```

Often times, we want to test our code using a combination of inputs. This can result in a very large number of tests that have to written and maintained. 
For example, above we only tested the happy path. But we also need to test the failing path

```python

...

def test_add_strs_fail() -> None:
	str1 = "Hello"
	str2 = "World!"
	
	with pytest.raises(ValueError) as e:
		result = add_strs(str1. str2)
```

In order to avoid having multiple tests, we can use ```pytest.mark.parameterize``` and let ```pytest``` handle the test generation for us.
The ```parameterize``` decorator allows us to define several sets of variables that will be passed as arguments to the test function.
At runtime each set will generate a new and independent test:


```python

import pytest
from str_utils import add_strs

@pytest.mark.parameterize("str1, str2, result", [("Hello", "World", "Hello_World"), ("Hello", "World1", ValueError)])
def test_add_strs_fail(str1: str. str2: str, result: str) -> None:
	
	assert add_strs(str1, str2) == result
```

## Using fixtures

We saw above how to use ```pytest``` to test out Python code. When we test large code bases, tests tend to become repetitive i.e. a large number
of these will share the same boilerplate  code. Consider for example testing a function that requires access to a database. In this case we will need to
specifiy the credentials to access the database. Removing the code duplication is something that we should, in general, strive towards and the test code base is no 
exception in this rule. ```pytest``` allows us to use fixtures that helps us mitigate code duplication in our test code base to a large extent. Fixtures are
functions decorated with the ```@pytest.fixture``` decorator. Inside a fixture function we can write whatever logic we think is needed. In order to get the idea, the following
fixture returns a connection to fictitious database 


```python

import pytest

@pytest.fixture(scope="session")
def get_test_db() -> MyDB:
	username: str = "testUser1"
	password: str = "letmein"
	return MyDB(username, password)
```

A fixture by default, it is recreated at the beginning of each single test function.
This may not something you always want to do. The ```scope``` parameter specifies the 
level at which the fixture will be recreated. The ```session``` value represents the highest
level and it means that the fixture is created once at the beginning of the whole test run.

We can now use this object as follows


```python
from typing import List

def get_user_orders(user: str, db_connection: MyDb) -> List[str]:

	return db_connection.execute_query(f"""SELECT order FROM orders WHERE emai={user}""")
```


```python

import pytest
from str_utils import add_strs

@pytest.mark.parameterize("user, result", [("alex", ["order1", "order2"]), ("invalidUser", [])])
def test_get_user_orders(user: str, result: List, get_test_db) -> None:
	
	assert get_user_orders(user, get_test_db) == result

```


Fixtures can also depend on other fixtures. This is shown below


Typically, we will store fixures in a file named ```conftest.py```. ```pytest``` will then automatically import the fixtures defined in
this file in the tests to be executed. 

## Summary


## References

1. <a href="https://docs.pytest.org/en/8.2.x/">pytest: helps you write better programs</a>
2. <a href="https://realpython.com/pytest-python-testing/">Effective Python Testing With Pytest</a>
