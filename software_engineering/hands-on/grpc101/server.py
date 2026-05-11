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