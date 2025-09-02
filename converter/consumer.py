import pika, sys, os
from pymongo import MongoClient
from gridfs import GridFS
from convert import to_mp3

def main():
    try:
        client = MongoClient(
            "host.minikube.internal",
            27017,
            username=os.environ.get("MONGO_USERNAME"),
            password=os.environ.get("MONGO_PASSWORD")
        )
        db_videos = client.gateway_db
        db_mp3 = client.mp3

        fs_videos = GridFS(db_videos)
        fs_mp3 = GridFS(db_mp3)

        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host="rabbitmq"
            )
        )
        channel = connection.channel()

        def callback(ch, method, _properties, body):
            err = to_mp3.start(body, fs_videos, fs_mp3, ch)
            if err:
                ch.basic_nack(delivery_tag = method.delivery_tag)
            else:
                ch.basic_ack(delivery_tag = method.delivery_tag)

        channel.basic_consume(
            queue = os.environ.get("VIDEO_QUEUE"),
            on_message_callback = lambda ch, method, properties, body: callback(ch, method, properties, body),
        )

        print(" [*] Waiting for messages. To exit press CTRL+C")

        channel.start_consuming()
    except Exception as e:
        print(f" [!] Error: {e}")
        try:
            sys.exit(1)
        except SystemExit:
            os._exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(" [*] Interrupted")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
