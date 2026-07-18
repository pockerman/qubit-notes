# qubit-note: Go Programming | Go Packages

## Overview


## Go packages

If you're coming from C++, Go packages are a bit like a combination of **C++ namespaces, translation units, and modules**, but with much stricter rules and much less configuration.

## The basic idea

A package is the unit of:

* code organization
* compilation
* visibility
* reuse

Everything in Go belongs to exactly one package.

For example:

```text
math/
    sqrt.go
    pow.go
    trig.go
```

Every file begins with

```go
package math
```

The compiler treats all of these files as one package.

---

## Think of it like C++

Imagine if every `.cpp` file that started with

```cpp
namespace math {
```

were automatically compiled together into a single library, and there were no header files.

That's roughly what a Go package is.

---

# Packages are directories

This is one of the biggest differences from C++.

A package corresponds to a directory.

```text
myproject/
    main.go
    util/
        strings.go
        math.go
```

```
main.go
```

```go
package main
```

```
util/strings.go
```

```go
package util
```

```
util/math.go
```

```go
package util
```

Both files belong to the same package because they're in the same directory.

---

# Importing packages

Suppose we have

```text
util/
    math.go
```

```go
package util

func Double(x int) int {
    return x * 2
}
```

Then another package can use it:

```go
package main

import "myproject/util"

func main() {
    fmt.Println(util.Double(10))
}
```

Notice that you qualify names with the package:

```go
util.Double()
```

Similar to

```cpp
math::sqrt()
```

---

# Exported vs unexported

Go has an extremely simple visibility rule.

If an identifier starts with an uppercase letter:

```go
func Double()
```

it's exported.

If it starts with lowercase:

```go
func helper()
```

it's private to the package.

Example:

```go
package util

func Double(x int) int {
    return helper(x)
}

func helper(x int) int {
    return x * 2
}
```

Outside:

```go
util.Double(5)
```

works.

```go
util.helper(5)
```

does not compile.

There are no keywords like

```cpp
public:
private:
protected:
```

Capitalization determines visibility.

---

# Files in the same package share everything

Suppose

```text
util/
    a.go
    b.go
```

`a.go`

```go
package util

func helper() {}
```

`b.go`

```go
package util

func Example() {
    helper()
}
```

This works even though they're different files.

They're effectively merged into one package during compilation.

---

# No header files

This surprises almost every C++ programmer.

Instead of

```text
math.h
math.cpp
```

you just write

```text
math.go
```

The compiler automatically knows every exported declaration.

So

```go
func Double(x int) int
```

acts as both the declaration and the definition.

---

# Package initialization

A package is initialized exactly once.

Suppose

```go
package config

var Version = loadVersion()
```

The first time another package imports `config`,

```go
import "config"
```

Go runs all package initialization.

It also supports

```go
func init() {
    ...
}
```

which runs automatically after package-level variables are initialized.

---

# Package names

Typically

```text
math/
strings/
fmt/
http/
json/
```

become

```go
math.Sqrt()

fmt.Println()

http.ListenAndServe()
```

The directory name is usually the package name.

---

# The special package: main

Every executable starts with

```go
package main
```

and

```go
func main() {
}
```

For example

```go
package main

import "fmt"

func main() {
    fmt.Println("Hello")
}
```

Every other package is a library.

Only `package main` produces an executable.

---

# Import paths

An import isn't just a package name; it's a module-qualified path.

For example:

```text
github.com/alice/project/math
```

contains

```go
package math
```

You import it as

```go
import "github.com/alice/project/math"
```

and use

```go
math.Sqrt()
```

The last path element is typically the package name.

---

# Aliases

If two packages have the same name:

```go
import (
    stdjson "encoding/json"
    fastjson "github.com/valyala/fastjson"
)
```

then

```go
stdjson.Marshal(...)

fastjson.Parser{}
```

This is similar to namespace aliases in C++.

---

# Blank imports

Sometimes you want initialization but won't reference any exported names:

```go
import _ "github.com/lib/pq"
```

The package is initialized, but you can't use it directly.

This is commonly used for plugin registration, database drivers, or image format registration.

---

# Dot imports

```go
import . "math"
```

Now you can write

```go
Sqrt(4)
```

instead of

```go
math.Sqrt(4)
```

This is generally discouraged because it makes it unclear where identifiers come from, though it's occasionally useful in tests.

---

# Comparing Go packages to C++ concepts

| C++                | Go                             |
| ------------------ | ------------------------------ |
| Namespace          | Package namespace              |
| Header + source    | Single `.go` file (no headers) |
| `public`/`private` | Uppercase/lowercase names      |
| Translation unit   | Entire package directory       |
| Static library     | Package                        |
| `using namespace`  | Dot import (rarely used)       |
| Namespace alias    | Import alias                   |

## A mental model for C++ developers

If you think in C++ terms, imagine this rule:

> Every directory is automatically compiled into a library. Every `.cpp` file in that directory shares the same namespace and can see all other declarations without headers. Functions whose names begin with a capital letter are the library's public API; everything else is internal. Other code uses the library by importing it and qualifying names with the package name.

That's essentially how Go packages work. This design eliminates much of the complexity around header files, include paths, forward declarations, and build configuration that C++ developers are accustomed to, making package boundaries the primary organizational mechanism in Go.

## References