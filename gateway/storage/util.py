import json, pika
from pika import spec
from pika.delivery_mode import DeliveryMode

def upload(file, fs, channel, access):
    try:
        fid = fs.put(file)
    except Exception as e:
        return f"Could not save file to database: {str(e)}", 500

    message = {
        "video_fid": str(fid),
        "mp3_fid": None,
        "user_email": access["user_email"],
    }

    try:
        channel.basic_publish(
            exchange='',
            routing_key='video',
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=DeliveryMode(spec.PERSISTENT_DELIVERY_MODE)
            ),
        )
    except Exception as e:
        fs.delete(fid)
        return f"Could not send message to the queue: {str(e)}", 500
