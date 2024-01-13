import grpc
from src.proto import bookaroo_pb2_grpc, bookaroo_pb2


class GRPC:
    @staticmethod
    def request(
            collection_name,
            operation, data,
            token,
            query
    ) -> bookaroo_pb2.Response:

        with grpc.insecure_channel("localhost:50051") as channel:
            stub = bookaroo_pb2_grpc.RequestProcessorStub(channel)
            request = bookaroo_pb2.Request(
                collectionName=collection_name,
                operation=operation,
                data=data,
                token=token,
                query=query
            )
            response = stub.process(request)
            return response
