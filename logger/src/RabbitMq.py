import pika
from fastapi import Depends
from schemas.PostBookarooLog import PostBookarooLog
from Database import Database


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

    @staticmethod
    def on_message_callback(channel, method, properties, body):
        print(f"""
    channel:   {channel}
    method:    {method}
    properties:{properties}
    body:      {body}""")
        print(body.decode("utf-8"))
        print(PostBookarooLog.from_json(body.decode("utf-8")))
        print(PostBookarooLog.from_json(body.decode("utf-8")))
        Database.insert_log(
            Depends(Database.get_db),
            PostBookarooLog.from_json(body.decode("utf-8"))
        )

    def start_consuming(self):
        conn_params = self.__conn_params__
        conn = pika.BlockingConnection(conn_params)
        channel = conn.channel()
        channel.queue_declare(queue="bookaroo-logs",
                              durable=True)

        channel.basic_consume(queue="bookaroo-logs",
                              auto_ack=True,
                              on_message_callback=self.on_message_callback)
        channel.start_consuming()
