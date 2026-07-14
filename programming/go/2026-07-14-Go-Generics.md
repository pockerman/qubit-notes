# qubit-note: Go Programming | Go Generics 101


Generics, introduced in **Go 1.18**, allow you to write functions and types that work with **multiple data types** while maintaining compile-time type safety.

Before generics, Go programmers often had to:

* Write the same function multiple times for different types.
* Use `interface{}` (now `any`), which sacrifices type safety and requires type assertions.

Generics solve both problems.

---

## Without generics

Suppose you want a function that returns the larger of two numbers.

You might write:

```go
func MaxInt(a, b int) int {
	if a > b {
		return a
	}
	return b
}

func MaxFloat(a, b float64) float64 {
	if a > b {
		return a
	}
	return b
}
```

Notice the code is identical except for the type.

---

## With generics

You can write it once:

```go
import "cmp"

func Max[T cmp.Ordered](a, b T) T {
	if a > b {
		return a
	}
	return b
}
```

Now you can use it for different types:

```go
fmt.Println(Max(3, 5))
fmt.Println(Max(2.3, 4.7))
fmt.Println(Max("cat", "dog"))
```

The compiler infers the type.

---

## What is `T`?

`T` is a **type parameter**.

```go
func Print[T any](value T) {
	fmt.Println(value)
}
```

Here:

* `T` can be any type.
* `any` is a constraint.

Equivalent to:

```go
interface{}
```

but used as a generic constraint.

Usage:

```go
Print(42)
Print("hello")
Print(true)
```

---

# Type constraints

Generics aren't magic—they need rules.

For example:

```go
func Add[T any](a, b T) T {
	return a + b
}
```

This won't compile.

Why?

Because not every type supports `+`.

Instead:

```go
import "golang.org/x/exp/constraints"

func Add[T constraints.Integer | constraints.Float](a, b T) T {
	return a + b
}
```

Now `T` must be a numeric type.

---

## Built-in constraints

Some common ones:

```go
cmp.Ordered
```

Allows:

* integers
* floats
* strings

because they can be compared using:

```go
<
>
<=
>=
```

---

## Generic structs

Generics also work on structs.

Example:

```go
type Stack[T any] struct {
	items []T
}
```

Methods:

```go
func (s *Stack[T]) Push(item T) {
	s.items = append(s.items, item)
}

func (s *Stack[T]) Pop() T {
	n := len(s.items)

	item := s.items[n-1]

	s.items = s.items[:n-1]

	return item
}
```

Usage:

```go
intStack := Stack[int]{}

intStack.Push(1)
intStack.Push(2)

fmt.Println(intStack.Pop())
```

Or

```go
stringStack := Stack[string]{}
```

No duplicated code.

---

# Generic interfaces

You can even parameterize interfaces.

```go
type Repository[T any] interface {
	Save(T) error
	Get(string) (T, error)
}
```

Then implement it:

```go
type UserRepository struct{}

func (UserRepository) Save(u User) error {
	...
}

func (UserRepository) Get(id string) (User, error) {
	...
}
```

---

# Your Gogi project

Suppose you currently have

```go
type VectorStorage interface {
	Add(...)
	Search(...)
}
```

Maybe later you'll have:

```go
type Repository[T any] interface {
	Create(T) error
	Update(T) error
	Delete(string) error
	Get(string) (T, error)
}
```

Then you can reuse it for

```go
Repository[Job]

Repository[Index]

Repository[User]

Repository[Document]
```

instead of writing four interfaces.

---

# Custom constraints

You can define your own.

```go
type Number interface {
	~int |
	~int64 |
	~float32 |
	~float64
}
```

Notice:

```go
~
```

means

> "Any type whose underlying type is..."

Then

```go
func Sum[T Number](values []T) T {
	var total T

	for _, v := range values {
		total += v
	}

	return total
}
```

---

# Multiple type parameters

Generics aren't limited to one.

```go
type Pair[K comparable, V any] struct {
	Key   K
	Value V
}
```

Usage:

```go
Pair[string, int]{
	Key: "age",
	Value: 47,
}
```

---

# Comparable

Sometimes you need a type that can be used as a map key.

```go
func Contains[T comparable](items []T, value T) bool {

	for _, item := range items {
		if item == value {
			return true
		}
	}

	return false
}
```

Now it works for

```go
Contains([]int{1,2,3},2)

Contains([]string{"a","b"},"a")
```

---

# Why not just use `any`?

Consider:

```go
func Print(v any)
```

Inside:

```go
fmt.Println(v)
```

Fine.

But:

```go
v + 1
```

is illegal.

You'd need

```go
switch t := v.(type) {
case int:
...
case float64:
...
}
```

Generics eliminate all that.

The compiler knows the exact type.

---

# When should you use generics?

Generics are most useful when you're writing **reusable libraries or infrastructure**, not ordinary business logic.

For example, in Gogi, good candidates include:

* Repository abstractions (`Repository[T]`).
* Collections like queues, stacks, or caches.
* Utility functions (e.g., `Max`, `Min`, `Filter`, `Map`).
* Generic data structures (LRU caches, priority queues).
* Common storage interfaces.

On the other hand, if you have a type that's inherently specific—such as a `JobsRepository` with methods like `GetPendingJobs()` or `MarkJobCompleted()`—using generics usually adds complexity without much benefit.

## A useful mental model

Think of generics as **templates for types**.

Without generics:

```go
func PrintInt(int)
func PrintString(string)
func PrintFloat(float64)
```

With generics:

```go
func Print[T any](T)
```

The Go compiler generates the appropriate type-specific implementation at compile time, giving you the flexibility of reusable code with the performance and type safety of regular Go.
