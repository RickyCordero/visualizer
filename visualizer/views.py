import time
import datetime
import json
from django.views import (
    View,
)
from django.views.generic.base import (
    TemplateView,
)
from django.http import (
    StreamingHttpResponse,
)
from kafka import KafkaConsumer

# kafka stuff
KAFKA_HOST = "kafka"
KAFKA_PORT = 9092
RECEIVE_TOPIC_NAME = "ableton_link_msgs"

# base string for sending SSE data through streaming http
SSE_BASE_DATA = '\ndata: {}\n\n'

STREAM_SLEEP_INTERVAL = 1 # how many seconds to sleep between each event stream kafka consumer read

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

def default(obj):
    if isinstance(obj, datetime.datetime):
        return {'_isoformat': obj.isoformat() }
    return obj

def js_serializer(v):
    """Serialize objects sent over HTTP."""
    if v is None:
        print("Received NoneType message, can't encode")
        return
    try:
        j = json.dumps(v, default=default)
        return j
    except TypeError as err:
        print("Unable to serialize the object")
        print(f"Encode error: {err}")
        return None

def create_consumer():
    return KafkaConsumer(
        bootstrap_servers   = [f"{KAFKA_HOST}:{KAFKA_PORT}"], # broker
        auto_offset_reset   = "latest",         # reset partition offsets upon OffsetOutOfRangeError
        value_deserializer  = kafka_deserializer,
    )

def link_event_stream():
    consumer = create_consumer()
    consumer.subscribe(RECEIVE_TOPIC_NAME)
    for message in consumer:
        # message.value contains the data being sent through kafka prior to encoding
        # i.e. it can be a string, or dict
        v = message.value
        data = js_serializer(v) # TODO: js_serializer or django.core.serializers.serialize?
        yield SSE_BASE_DATA.format(data)
        # time.sleep(STREAM_SLEEP_INTERVAL)

class APILinkStreamView(View):

    def get(self, request, *args, **kwargs):
        response = StreamingHttpResponse(link_event_stream())
        response['Content-Type'] = 'text/event-stream'
        return response

class IndexView(TemplateView):
    template_name = "visualizer/visualizer.html"