# qubit-note: C++ Programming | Symmetric Transfer in C++ Coroutines


## Overview



## Symmetric Transfer in C++ Coroutines


Symmetric transfer is an optimization and control-flow technique in C++20 coroutines that lets one coroutine directly transfer execution to another coroutine **without first returning to the caller or scheduler**.

The idea is easiest to understand by contrasting it with the "normal" coroutine flow.

## Without symmetric transfer

Suppose you have three coroutines:

```
main
  ↓
Coroutine A
  ↓
Coroutine B
```

When `B` finishes, the typical flow is:

```
main
  ↓
A
  ↓
B completes
  ↑
A resumes
  ↑
main continues
```

Every coroutine completion unwinds one level of the stack of coroutine resumptions.

If A immediately wants to resume another coroutine after B finishes, you get a sequence like:

```
B finishes
↓
Resume A
↓
A resumes C
↓
Suspend A
```

This creates unnecessary bouncing between coroutines.

---

## With symmetric transfer

Instead, B can say:

> "When I'm done, don't resume A first. Resume C directly."

The flow becomes

```
main
  ↓
A
  ↓
B completes
  ↓
C resumes directly
```

A never runs in the middle merely to forward execution.

Execution is *transferred* directly from one coroutine to another.

---

## Why this matters

Imagine implementing an async runtime.

Without symmetric transfer:

```
Task1 finishes

resume continuation

continuation resumes Task2

Task2 suspends

return

return
```

Lots of intermediate resumes and returns occur.

With symmetric transfer:

```
Task1 finishes
        │
        ▼
Task2 resumes immediately
```

No unnecessary scheduler hop.

This can significantly reduce

* context switches
* recursion depth
* overhead
* stack growth

---

## How it works

The coroutine machinery revolves around the return value of

```cpp
await_suspend(std::coroutine_handle<> awaiting);
```

Normally, people see

```cpp
void await_suspend(...)
```

or

```cpp
bool await_suspend(...)
```

But there is a third overload:

```cpp
std::coroutine_handle<>
await_suspend(std::coroutine_handle<> awaiting);
```

Returning a coroutine handle tells the runtime:

> "Resume this coroutine next."

This is symmetric transfer.

For example

```cpp
std::coroutine_handle<>
await_suspend(std::coroutine_handle<> awaiting)
{
    return continuation;
}
```

instead of

```cpp
continuation.resume();
return;
```

The runtime performs the transfer itself.

---

## Example

Suppose you have

```cpp
task<int> foo();

task<void> bar()
{
    int x = co_await foo();
}
```

Internally, the flow is roughly

```
bar
 │
 │ co_await foo()
 ▼
foo runs
 │
 │ finishes
 ▼
resume bar
```

Without symmetric transfer, the runtime effectively does

```
foo completes

↓

return to runtime

↓

runtime resumes bar
```

With symmetric transfer, `foo`'s final suspend can return the handle for `bar`, allowing the runtime to jump directly into `bar`.

---

## `final_suspend()` is where it's commonly used

Many coroutine libraries implement something like

```cpp
auto final_suspend() noexcept
{
    return final_awaiter{};
}
```

where

```cpp
struct final_awaiter
{
    std::coroutine_handle<>
    await_suspend(std::coroutine_handle<promise_type> h) noexcept
    {
        return h.promise().continuation;
    }

    bool await_ready() noexcept
    {
        return false;
    }

    void await_resume() noexcept {}
};
```

When the coroutine reaches the end:

```
Coroutine A finishes
        │
        ▼
final_suspend
        │
        ▼
return continuation handle
        │
        ▼
Runtime resumes continuation immediately
```

Notice there is no intermediate resume of some scheduler coroutine.

---

## Why is it called "symmetric"?

Historically, coroutine systems distinguish between two styles:

**Asymmetric coroutines**

A coroutine always yields back to its caller.

```
A
 ↓
B
 ↑
A
```

This is how generators typically behave.

**Symmetric coroutines**

A coroutine can transfer control to **any** coroutine.

```
A
 ↓
B
 ↓
C
 ↓
D
 ↓
A
```

The transfer isn't constrained to returning to the immediate caller.

C++ coroutines are fundamentally asymmetric, but the `std::coroutine_handle`-returning form of `await_suspend()` enables this symmetric transfer optimization.

---

## A practical mental model

Think of the difference like this.

Without symmetric transfer:

```
A:
    call B

B:
    return

A:
    call C
```

Execution repeatedly returns to the middleman.

With symmetric transfer:

```
A:
    transfer to B

B:
    transfer to C

C:
    transfer to D
```

Each coroutine hands execution directly to the next, avoiding unnecessary detours.

## When you'll encounter it

Symmetric transfer is commonly used in high-performance coroutine libraries such as `cppcoro`, Boost.Asio's coroutine support, and many custom executors. It's especially valuable for `task<T>` implementations because a completed task can immediately resume its awaiting coroutine, eliminating extra scheduling overhead and preventing deep chains of coroutine completions from causing recursive `resume()` calls or excessive stack growth.
