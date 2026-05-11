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
