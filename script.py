import json
import time
from datetime import datetime
from decimal import Decimal
from kafka import KafkaProducer
import LinkToPy


# path = "/mnt/c/Users/ricky/Carabiner.exe"
path = '/mnt/c/Users/ricky/Carabiner_Linux_x64'

link = LinkToPy.LinkInterface(f"{path}")
print(link.now())

KAFKA_HOST = "kafka"
KAFKA_PORT = 9092
SEND_TOPIC_NAME = "ableton_link_msgs"

def default(obj):
    if isinstance(obj, datetime):
        return {'_isoformat': obj.isoformat() }
    if isinstance(obj, Decimal):
        return str(obj)
    return obj

def kafka_serializer(v):
    if v is None:
        print("Received NoneType message, can't encode")
        return
    try:
        return json.dumps(v, default=default).encode('utf-8')
    except TypeError as err:
        print("Unable to serialize the object")
        print(f"Encode error: {err}")
        return None

PRODUCER = KafkaProducer(
    bootstrap_servers = [f"{KAFKA_HOST}:{KAFKA_PORT}"],
    value_serializer  = kafka_serializer
)


while 1:
    link.status()
    message = link.bpm_
    print(link.bpm_)
    PRODUCER.send(
        SEND_TOPIC_NAME,
        message,
    )
    time.sleep(0.1)