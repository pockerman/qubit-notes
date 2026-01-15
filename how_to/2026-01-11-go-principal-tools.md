# qubit-note: Go Progamming Series | Go Principal Tools


## Overview

In this qubit note we will look into some of the tools available in the Go programming language.

- ```go build```
- ```go test```
- ```go run```
- ```go vet```
- ```go fmt```

**keywords** Programmin, Go

## Go principal tools

#### go test

As the name suggests, the tool ```go test``` can be used to run unit tests in Go


Note that ```go test``` has a built-in feature called Go race detection that can detect and identify race
conditions in your Go code. Below is an example illustrating this

```
package main
import (
     "testing"
)
func TestPackItems(t *testing.T) {
     totalItems := PackItems(2000)
     expectedTotal := 2000
     if totalItems != expectedTotal {
          t.Errorf("Expected total: %d, Actual total: %d",
expectedTotal, totalItems)
     }
}
```

Run the detector using

```
go test -race
```

## Summary

## References