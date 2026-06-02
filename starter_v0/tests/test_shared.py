from __future__ import annotations

import unittest
from unittest.mock import Mock, patch

import requests

from tools._shared import request_with_retry


class RequestWithRetryTests(unittest.TestCase):
    def test_retries_timeout_then_returns_success(self) -> None:
        response = Mock(status_code=200)
        with patch("tools._shared.requests.request", side_effect=[requests.ReadTimeout("slow"), response]) as request:
            with patch("tools._shared.time.sleep") as sleep:
                self.assertIs(request_with_retry("GET", "https://example.com"), response)
        self.assertEqual(request.call_count, 2)
        sleep.assert_called_once_with(0.5)

    def test_retries_retryable_status_then_returns_success(self) -> None:
        busy = Mock(status_code=503)
        response = Mock(status_code=200)
        with patch("tools._shared.requests.request", side_effect=[busy, response]) as request:
            with patch("tools._shared.time.sleep") as sleep:
                self.assertIs(request_with_retry("POST", "https://example.com"), response)
        self.assertEqual(request.call_count, 2)
        sleep.assert_called_once_with(0.5)

    def test_does_not_retry_non_retryable_status(self) -> None:
        forbidden = Mock(status_code=403)
        with patch("tools._shared.requests.request", return_value=forbidden) as request:
            with patch("tools._shared.time.sleep") as sleep:
                self.assertIs(request_with_retry("GET", "https://example.com"), forbidden)
        request.assert_called_once()
        sleep.assert_not_called()


if __name__ == "__main__":
    unittest.main()
