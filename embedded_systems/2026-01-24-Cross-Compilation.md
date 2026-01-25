# qubit-note: Cross Compiling C++ on Linux

## Overview

When working with embedded system most often than not, we need to work with two types of environments;
the environment where we write and build the code and the environment that runs the software.
In this qubit note we will look into the topic of cross compilation C++ programs on Linux platforms. Specifically,
we will build a simple hello program using the ```g++-aarch64-linux-gnu``` toolchain. We will then upload and execute
the binary on a Raspberry Pi 5 board. This is a board having a 64-bit quad-core Cortex-A76 processor.

**keywords** Cross-compilation, C++, Raspberry Pi, ARM

## Cross Compiling C++ on Linux

We will be using Docker to create our build environment. The Dockerfile is shown below:

```
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    build-essential \
    gcc-aarch64-linux-gnu \
    g++-aarch64-linux-gnu \
    binutils-aarch64-linux-gnu \
    pkg-config \
    cmake \
    make \
    git \
    nano \
    file \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

ENV CC=aarch64-linux-gnu-gcc \
    CXX=aarch64-linux-gnu-g++ \
    AR=aarch64-linux-gnu-ar \
    AS=aarch64-linux-gnu-as \
    LD=aarch64-linux-gnu-ld \
    STRIP=aarch64-linux-gnu-strip \
    CFLAGS="-march=armv8-a" \
    CXXFLAGS="-march=armv8-a"

WORKDIR /work

CMD ["/bin/bash"]

```


The build environment will contain the following tools

- ARM GNU Toolchain version
- CMake and the make utility
- Nano editor
- Git

Build the image using

```
docker build   -t armhf-cross .
```

Start the container in a detached mode

```
docker run -d -it --name dev_env armhf-cross:latest
```

Open a shell and log into the running container:

```
docker exec -it dev_env /bin/bash
```

Check the version of the ARM GNU toolchain

```
aarch64-linux-gnu-g++ --version
```

Inside the container, use the nano editor to create the example below:


```
#include <iostream>

int main(){
std::cout<<"Hello world"<<std::endl;
}

```

Buld the executable:

```
aarch64-linux-gnu-g++ example.cpp -o example
```

We have also installed in the container the ```file``` command. We can use it to make sure that the produced executable is an ARM executable:

```
file ./example
```

This should print something like the following:

```
./example: ELF 32-bit LSB pie executable, ARM, EABI5 version 1 (SYSV), dynamically linked, interpreter /lib/ld-linux-armhf.so.3, BuildID[sha1]=4aef14e415c483a3286316dfe63e85ab1311707b, for GNU/Linux 3.2.0, not stripped
```

Let's now upload the executable on a Raspeberry Pi board. This is simple with ssh/scp

```
scp example <YOUR-USERNAME>@<YOUR-PI-IP>:/home

```

Log in your Pi board and execute the uploaded program. Note the you may have to make the file executable:

```
chmod +x example
```

## Summary

In this qubit note we discussed cross compilation on Linux. Specifically, we used the ```g++-arm-linux-gnueabihf``` toolchain to build a small program
that can run on a Raspberry Pi board. Notice that in this note we assumed that an OS exists on the board. We will discuss in another note how to
work when there is no OS on the board. 

## References

1. Amar Mahmutbegovic, _C++ in embedded Systems. A practical transition from C to modern C++_, Packt Publications.
2. Igor Viarcheichyk, _Embedded programming with modern C++ Cookbok_, Packt Publications.