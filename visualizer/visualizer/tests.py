import json
from unittest.mock import AsyncMock, MagicMock, patch
from django.test import SimpleTestCase
from django.urls import reverse

class VisualizerSyncTests(SimpleTestCase):
    def test_round_trip_serialization(self):
        """Verify that basic type formats and serialization structure remain consistent."""
        payload = {
            "bpm": 120.0,
            "beat": 45.5,
            "timestamp": 1687299000.123
        }
        serialized = json.dumps(payload)
        deserialized = json.loads(serialized)
        
        self.assertEqual(deserialized["bpm"], 120.0)
        self.assertEqual(deserialized["beat"], 45.5)
        self.assertEqual(deserialized["timestamp"], 1687299000.123)

    @patch("zmq.asyncio.Context")
    async def test_api_link_stream_view(self, mock_zmq_context):
        """Test that the Event Stream endpoint responds with correct HTTP parameters and consumes ZMQ messages."""
        # Mock ZMQ sockets and messages
        mock_context_instance = mock_zmq_context.return_value
        mock_socket = MagicMock()
        mock_context_instance.socket.return_value = mock_socket
        
        # Make recv_string (an async method) yield a test message, then raise ValueError to break the infinite loop
        test_payload = '{"bpm": 128.0, "beat": 12.0, "timestamp": 1687299500.0}'
        mock_socket.recv_string = AsyncMock(side_effect=[test_payload, ValueError("Stop loop")])
        
        # Request the URL using the Django async test client
        url = reverse("api-link-view")
        response = await self.async_client.get(url)
        
        # Verify response structure
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/event-stream")
        
        # Read stream output by iterating until the ValueError terminates it
        chunks = []
        try:
            async for chunk in response.streaming_content:
                chunks.append(chunk)
        except ValueError:
            pass  # Expected exception to exit the infinite generator
            
        stream_content = b"".join(chunks).decode("utf-8")
        self.assertIn(f"data: {test_payload}", stream_content)


