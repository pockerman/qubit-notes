Simple gRPC ```Hello World``` 



Install the python requirements:

```
pip install -r requirements.txt
```

Install the Go gRPC tools.

```
go install google.golang.org/protobuf/cmd/protoc-gen-go@latest
go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@latest
```

Note you will need Go installed on your machine for the above.


Generate the code. Create the directories ```./grpc/go``` and ```./grpc/python```

```
protoc --go_out=./grpc101/go --go-grpc_out=./grpc101/go ./proto/message.proto
python -m grpc_tools.protoc -I./proto --python_out=./grpc101/python --grpc_python_out=./grpc101/python ./proto/message.proto


cd grpc101/python

python -m grpc_tools.protoc -I../../proto --python_out=. --grpc_python_out=. ../../proto/message.proto

```

Run the Python server

```
PYTHONPATH=./grpc101/python python server.py server.py
```


Run the Go client

```
go mod init grpc101
go mod tidy
go run client.go
```