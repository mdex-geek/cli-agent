import json
from unittest.mock import Mock, patch
import pytest
from pieces.copilot.pieces_ask_websocket import AskWebsocket

class TestWebSocketManager:
    @pytest.fixture
    def mock_websocket(self):
        with patch('websocket.WebSocketApp') as mock:
            yield mock

    @pytest.fixture
    def ws_manager(self):
        return AskWebsocket()

    def test_init(self, ws_manager):
        assert ws_manager.ws is None
        assert not ws_manager.is_connected
        assert ws_manager.live is None

    def test_on_message(self, ws_manager):
        sample_message = json.dumps({
            'question': {
                'answers': {
                    'iterable': [{'text': 'Test answer'}]
                }
            },
            'status': 'COMPLETED'
        })
        ws_manager.on_message(None, sample_message)

    def test_on_error(self, ws_manager):
        ws_manager.on_error(None, "Test error")
        assert not ws_manager.is_connected

    def test_on_close(self, ws_manager):
        ws_manager.on_close(None, None, None)
        assert not ws_manager.is_connected

    def test_start_websocket_connection(self, ws_manager, mock_websocket):
        ws_manager._start_ws()
        mock_websocket.assert_called_once_with(
            "ws://localhost:1000/qgpt/stream",
            on_open=ws_manager.on_open,
            on_message=ws_manager.on_message,
            on_error=ws_manager.on_error,
            on_close=ws_manager.on_close
        )

    def test_send_message(self, ws_manager, mock_websocket):
        ws_manager.ws = Mock()
        ws_manager.is_connected = True
        ws_manager.query = "Test query"
        ws_manager.model_id = "Test model"
        ws_manager.conversation = "Test"
        ws_manager.send_message()

        expected_message = {
            "question": {
                "query": "Test query",
                "relevant": {"iterable": []},
                "model": "Test model"
            },
            "conversation": "Test"
        }
        ws_manager.ws.send.assert_called_with(json.dumps(expected_message))
