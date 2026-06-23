import logging
import zmq
from django.views.generic.base import TemplateView
from django.http import StreamingHttpResponse

logger = logging.getLogger("views")


def link_event_stream():
    import sys
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    
    # Configure SUB socket to subscribe to all messages
    socket.setsockopt_string(zmq.SUBSCRIBE, "")
    
    # Setup candidate connections for ZeroMQ Publisher:
    if sys.platform == 'win32':
        endpoints = ["tcp://127.0.0.1:5555"]
    else:
        endpoints = [
            "tcp://producer:5555",
            "tcp://127.0.0.1:5555",
            "tcp://host.docker.internal:5555"
        ]
    
    for endpoint in endpoints:
        logger.info(f"Connecting ZeroMQ SUB to {endpoint}")
        try:
            socket.connect(endpoint)
        except Exception as e:
            logger.warning(f"Failed to connect ZeroMQ to endpoint {endpoint}: {e}")

    try:
        while True:
            # Synchronous blocking recv (runs on the WSGI thread)
            msg = socket.recv_string()
            logger.info(f"Received message from ZMQ: {msg}")
            yield f"data: {msg}\n\n"
    except Exception as e:
        logger.error(f"Error in ZMQ subscriber: {e}")
    finally:
        logger.info("Cleaning up ZeroMQ subscriber socket and context.")
        socket.close()
        context.term()


def api_link_stream_view(request):
    response = StreamingHttpResponse(link_event_stream())
    response['Content-Type'] = 'text/event-stream'
    response['Cache-Control'] = 'no-cache'
    return response


class IndexView(TemplateView):
    template_name = "visualizer/visualizer.html"