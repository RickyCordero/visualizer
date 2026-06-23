import asyncio
import logging
import zmq.asyncio
from django.views import (
    View,
)
from django.views.generic.base import (
    TemplateView,
)
from django.http import (
    StreamingHttpResponse,
)

logger = logging.getLogger("views")


async def link_event_stream():
    import sys
    context = zmq.asyncio.Context()
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
            try:
                # Cooperative non-blocking wait using native asyncio loop
                msg = await socket.recv_string()
                logger.info(f"Received message from ZMQ: {msg}")
                yield f"data: {msg}\n\n"
            except zmq.ZMQError as ze:
                logger.error(f"ZeroMQ Socket Error: {ze}")
                await asyncio.sleep(1.0)
    except asyncio.CancelledError:
        logger.info("SSE client connection closed, stream generator cancelled.")
    finally:
        logger.info("SSE client disconnected. Cleaning up ZeroMQ subscriber socket and context.")
        socket.close()
        context.term()


class AsyncOnly:
    def __init__(self, ait):
        self._ait = ait

    def __aiter__(self):
        return self._ait.__aiter__()


async def api_link_stream_view(request):
    response = StreamingHttpResponse(AsyncOnly(link_event_stream()))
    response['Content-Type'] = 'text/event-stream'
    return response


class IndexView(TemplateView):
    template_name = "visualizer/visualizer.html"