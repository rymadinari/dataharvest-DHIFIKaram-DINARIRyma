from unittest.mock import MagicMock, patch

import pytest
import requests

from dataharvest.fetcher import Fetcher, FetchError
from dataharvest.middleware import LoggingMiddleware, RetryMiddleware


class FakeConfig:
    class fetcher:
        delay = 0.0
        retries = 3
        timeout = 5
        user_agent = "DataHarvest/1.0"


def make_response(status_code=200, text="<html>ok</html>"):
    response = MagicMock()
    response.status_code = status_code
    response.text = text
    return response


def test_fetch_returns_nonempty_str_on_success():
    config = FakeConfig()
    session = MagicMock()
    session.get.return_value = make_response(200, "<html>hello</html>")

    fetcher = Fetcher(config, middlewares=[LoggingMiddleware()], session=session)
    html = fetcher.fetch("https://example.com/")

    assert isinstance(html, str)
    assert html != ""


def test_fetch_raises_fetcherror_after_retries_exhausted():
    config = FakeConfig()
    session = MagicMock()
    session.get.side_effect = requests.ConnectionError("boom")

    retry = RetryMiddleware(config, base_delay=0.0)
    fetcher = Fetcher(config, middlewares=[retry], session=session)

    with pytest.raises(FetchError):
        fetcher.fetch("https://example.com/")

    # 1 essai initial + retries
    assert session.get.call_count == config.fetcher.retries + 1


def test_fetch_uses_configured_user_agent():
    config = FakeConfig()
    session = MagicMock()
    session.get.return_value = make_response(200, "<html></html>")

    fetcher = Fetcher(config, middlewares=[], session=session)
    fetcher.fetch("https://example.com/")

    _, kwargs = session.get.call_args
    assert kwargs["headers"]["User-Agent"] == "DataHarvest/1.0"


def test_fetch_all_respects_delay(monkeypatch):
    config = FakeConfig()
    config.fetcher.delay = 0.01
    session = MagicMock()
    session.get.return_value = make_response(200, "<html></html>")

    sleep_calls = []
    monkeypatch.setattr("dataharvest.fetcher.time.sleep", lambda s: sleep_calls.append(s))

    fetcher = Fetcher(config, middlewares=[], session=session)
    results = fetcher.fetch_all(["https://example.com/1", "https://example.com/2"])

    assert len(results) == 2
    assert 0.01 in sleep_calls
