import datetime
from kafka import KafkaConsumer

KAFKA_HOST = "127.0.0.1"
KAFKA_PORT = 9092
RECEIVE_TOPIC_NAME = "ableton_link_msgs"

def object_hook(obj):
    """Used for deserializing datetime objects."""
    _isoformat = obj.get('_isoformat')
    if _isoformat is not None:
        t1 = datetime.datetime.fromisoformat(_isoformat)
        return t1
    return obj

def kafka_deserializer(v):
    """Deserialize objects sent over Kafka."""
    if v is None:
        print("Received NoneType message, can't decode")
        return
    try:
        res = json.loads(v.decode('utf-8'), object_hook=object_hook)
        return res
    except json.decoder.JSONDecodeError as err:
        print('Unable to decode: %s', v)
        print(f"Decode error: {err}")
        return None

def create_consumer():
    return KafkaConsumer(
        bootstrap_servers   = [f"{KAFKA_HOST}:{KAFKA_PORT}"], # broker
        auto_offset_reset   = "latest",         # reset partition offsets upon OffsetOutOfRangeError
        value_deserializer  = kafka_deserializer,
    )

consumer = create_consumer()
consumer.subscribe(RECEIVE_TOPIC_NAME)
for message in consumer:
    # print(message)
    # message.value contains the data being sent through kafka prior to encoding
    # i.e. it can be a string, or dict
    v = message.value
    print(v)
    # data = js_serializer(v) # TODO: js_serializer or django.core.serializers.serialize?
