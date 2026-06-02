from __future__ import annotations

import os
import unittest
from unittest.mock import Mock, patch

import requests

from tools._twitter import DEFAULT_TWITTER_HOST, twitter_get


class TwitterGetTests(unittest.TestCase):
    def test_requires_api_key(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(RuntimeError, "Missing RAPIDAPI_KEY"):
                twitter_get("/timeline.php", {"screenname": "sama"})

    def test_403_explains_subscription_requirement(self) -> None:
        response = Mock(status_code=403)
        with patch.dict(os.environ, {"RAPIDAPI_KEY": "test"}, clear=True):
            with patch("tools._twitter.requests.get", return_value=response):
                with self.assertRaisesRegex(RuntimeError, "subscribed to Twitter API45"):
                    twitter_get("/timeline.php", {"screenname": "sama"})

    def test_404_explains_expected_host(self) -> None:
        response = Mock(status_code=404)
        with patch.dict(os.environ, {"RAPIDAPI_KEY": "test", "RAPIDAPI_TWITTER_HOST": "wrong.example"}, clear=True):
            with patch("tools._twitter.requests.get", return_value=response):
                with self.assertRaisesRegex(RuntimeError, DEFAULT_TWITTER_HOST):
                    twitter_get("/timeline.php", {"screenname": "sama"})

    def test_429_explains_quota_requirement(self) -> None:
        response = Mock(status_code=429)
        with patch.dict(os.environ, {"RAPIDAPI_KEY": "test"}, clear=True):
            with patch("tools._twitter.requests.get", return_value=response):
                with self.assertRaisesRegex(RuntimeError, "quota and rate limit"):
                    twitter_get("/search.php", {"query": "OpenAI"})

    def test_returns_json_for_success(self) -> None:
        response = Mock(status_code=200)
        response.raise_for_status.return_value = None
        response.json.return_value = {"timeline": []}
        with patch.dict(os.environ, {"RAPIDAPI_KEY": "test"}, clear=True):
            with patch("tools._twitter.requests.get", return_value=response):
                self.assertEqual(twitter_get("/timeline.php", {"screenname": "sama"}), {"timeline": []})

    def test_wraps_connection_failure_with_host_context(self) -> None:
        with patch.dict(os.environ, {"RAPIDAPI_KEY": "test"}, clear=True):
            with patch("tools._twitter.requests.get", side_effect=requests.ConnectionError("reset")):
                with patch("tools._twitter.time.sleep") as sleep:
                    with self.assertRaisesRegex(RuntimeError, f"request failed for host {DEFAULT_TWITTER_HOST}"):
                        twitter_get("/timeline.php", {"screenname": "sama"})
        sleep.assert_called_once_with(0.5)

    def test_retries_connection_failure_once(self) -> None:
        response = Mock(status_code=200)
        response.raise_for_status.return_value = None
        response.json.return_value = {"timeline": []}
        with patch.dict(os.environ, {"RAPIDAPI_KEY": "test"}, clear=True):
            with patch("tools._twitter.requests.get", side_effect=[requests.ConnectionError("reset"), response]) as request:
                with patch("tools._twitter.time.sleep") as sleep:
                    self.assertEqual(twitter_get("/timeline.php", {"screenname": "sama"}), {"timeline": []})
        self.assertEqual(request.call_count, 2)
        sleep.assert_called_once_with(0.5)


if __name__ == "__main__":
    unittest.main()
