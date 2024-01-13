from RabbitMq import RabbitMq
from Database import Database

if __name__ == "__main__":
    # Database.init_db()
    RabbitMq().start_consuming()
