# qubit-notes: Go | Variables

## Overview

Every programming language supports a number of variable types such as integers and floating point numbers. Go is no difference.
In this note we give a brief overview of the types of variables that the Go programming language supports


## Variables

Go supports a number of variable types. These are listed below


- bool
- string
- integers (int, int8, int16, int32, int64, uint, uint8, uint16, uint32, uint64, uintptr)
- byte which is an alias to uint8
- rune  which is an alias for int32 and represents a Unicode code point
- float32, float64
- complex64, complex128

As you can probably guess, the size (8, 16, 32 and so on) indicates how many bits in memory will be used to store the variable.


Go is a statically typed but it can also infer types based on expressions. Below is how we could declare a variable of a given type

```
var myVar int
```

Or we can also initialized it

```
var myHeight float32 = 178.0
```

---
**Remark No semicolons**

Some programming languages e.g. C++ and Java require a semicolon in order to declare that a declaration is finished. Go does not

---

Go uses default values for uninitalized variables. Run the following program:

```
package main

import "fmt"

func main() {
	fmt.Println("sow how to create variables in Go")

	// variable declaration without initialization
	var myVar int
	fmt.Println("Value of myVar: ", myVar)
}
```

As mentioned above, Go can figure out the type of a variable for us, similar to ```auto``` keyword in C++. However, in order for this to happen
we obviously need to initialize the variable. Here is how wwe can use this feature.


```
// this is still a statically typed variable
myVar := 1
```

---
**Remark: operator :=**

The operator ```:=``` is called the short assignement operator in Go.

---

Go  also allows us to declare multiple variables in the same line. Furthermore, this variables can have different types. This is shown below:

```
myInt, myFloat, myStr := 1, 1.0, "1.0"
```

We can also convert from one variable type to another an operation that is called casting. You need to be careful when performing thses sort of operations. Here is how you can do casting in Go


```
accountAge := 2.6
accountAgeInt := int(accountAge)
```

Go  also supports ```const``` variables:

```
const myName = "Alex"
```
 
You cannot mutate ```const``` declared variables. You can also cannot use the short assignment operator. Furthermore, you cannot declare a constant that can only be computed at runtime.



## Summary

## References