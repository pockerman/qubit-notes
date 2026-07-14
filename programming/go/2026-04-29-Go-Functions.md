# qubit-note: Go | Functions

## Overview

in this lesson we will look into functions in Go.


## Functions

The basic syntax of a function in Go is as follows

```
func funcName(param1 Type1, param2 Type2) ReturnType{
	// function body
}

or 


func funcName(param1, param2 Type1, param3 Type2) ReturnType{
	// function body
}
```

Notice that the type of the parameter comes after its name. Below are some simple examples

```
func addIntegers(a int, b int) int{
	return a + b
}

func speak(message: string){
	fmt.Printf("%s", message)
}
```

## Summary

## References