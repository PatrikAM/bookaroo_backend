import grpc
from concurrent import futures
import time

from proto import bookaroo_pb2_grpc
from servicer import BookarooServicer

server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))


def serve():
    # bookaroo_pb2_grpc.Rating.lastRating()

    bookaroo_pb2_grpc.add_RequestProcessorServicer_to_server(
        BookarooServicer(),
        server
    )
    server.add_insecure_port("[::]:50051")
    server.start()
    time.sleep(600_000)


if __name__ == "__main__":
    serve()
