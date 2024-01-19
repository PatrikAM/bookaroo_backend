import pika


class RabbitMq:
    __conn_params__ = pika.ConnectionParameters(host='rabbitmq')
    # __conn_params__ = pika.ConnectionParameters(host='127.0.0.1')
    __routing_key__ = 'bookaroo-logs'

    def publish(self, msg: str):
        conn = pika.BlockingConnection(self.__conn_params__)
        channel = conn.channel()
        channel.basic_publish(
            exchange='',
            routing_key=self.__routing_key__,
            body=msg
        )
        conn.close()
