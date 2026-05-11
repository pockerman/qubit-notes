# qubit-note: API Basics | Hands On | gRPC 

## Overview

In this qubit note we will discuss the gRPC API architecture. We will have a Python service acting as a server and a Go service acting as 
the client. You will need to have both Python and Go installed on your machine.



## gRPC 101

gRPC was developed by Google in 2016. It uses protocol buffers to encode and send data over the wire by default.
Protocol buffers are both platform and language agnostic constructs for encoding structured data.
Protocal buffers support strongly typed schema definition. Bellow is an example:

```
message Person{
	string name = 1;
	string surname = 2;
	int32 age = 3;
}
```


---
**Remark**

Protocol buffers are serialized and send as binaries accorss the network

---

A gRPC service is also defined in a proto file:

```
service  RegisterPerson{

	rpc Register(Person) returns (RegistrationResponse){}
}

message Person{
	string name = 1;
	string surname = 2;
	int32 age = 3;
}

message RegistrationResponse{
	string status = 1;
}

````

Now that we have an understandin of what gRPC is, let's implement a simple example. We will have a Python service acting as a server and a Go service acting as 
the client. You will need to have both Python and Go installed on your machine.

The following is the definition of the structures the two services will be using.

```
syntax = "proto3";

package grpc101;

option go_package = "grpc101/proto;proto";


service Service {
  rpc Ask(Request) returns (stream Response);
}

message Request {
  string query = 1;
}

message Response {
  string response = 1;
}
```

These have to be compiled using the ```protoc``` compiler. Below is how to do this for Python and Go.

```
protoc --go_out=./grpc101/go --go-grpc_out=./grpc101/go ./proto/message.proto
python -m grpc_tools.protoc -I./proto --python_out=./grpc101/python --grpc_python_out=./grpc101/python ./proto/message.proto
```

---
**Remark**

You will need to create a directory ```grpc101``` and within it the directories ```grpc/go``` and ```grpc/python```

---

Below are the drivers for the two services:

```
import time
import grpc
from concurrent import futures

import grpc101.python.message_pb2 as message_pb2
import grpc101.python.message_pb2_grpc as message_pb2_grpc


class Service(message_pb2_grpc.ServiceServicer):

    def Ask(self, request, context):
        print(f"Received Query: {request.query}")

        text = f"Answer for '{request.query}'"
        text += " I don't know what are you talking about"

        # simulate streaming tokens
        for word in text.split():
            yield message_pb2.Response(response=word + " ")
            time.sleep(0.1)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    message_pb2_grpc.add_ServiceServicer_to_server(Service(), server)

    server.add_insecure_port("[::]:50051")
    server.start()

    print("Python gRPC server running on :50051")

    server.wait_for_termination()


if __name__ == "__main__":
    serve()
```

```
package main

import (
	"context"
	"fmt"
	"io"
	"log"
	"time"

	pb "grpc101/grpc101/go/grpc101/proto"

	"google.golang.org/grpc"
)

func main() {
	conn, err := grpc.Dial("localhost:50051", grpc.WithInsecure())
	if err != nil {
		log.Fatal("did not connect:", err)
	}
	defer conn.Close()

	client := pb.NewServiceClient(conn)

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	stream, err := client.Ask(ctx, &pb.Request{
		Query: "Explain DDD to me",
	})
	if err != nil {
		log.Fatal(err)
	}

	fmt.Println("Streaming response:")

	for {
		res, err := stream.Recv()
		if err == io.EOF {
			break
		}
		if err != nil {
			log.Fatal(err)
		}

		fmt.Print(res.Response)
	}

	fmt.Println("\nDone.")
}

```

Open a terminal and run 

```
PYTHONPATH=./grpc101/python python server.py server.py
```

then open another terminal and type

```
go mod init grpc101
go mod tidy
go run client.go
```

## Summary


## References

1. <a href="https://www.youtube.com/watch?v=hVrwuMnCtok">What is gRPC? (Remote Procedure Calls)</a>
2. <a href="https://www.youtube.com/watch?v=gnchfOojMk4">What is RPC? gRPC Introduction.</a>