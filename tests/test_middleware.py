import time

from dataharvest.middleware import LoggingMiddleware, RateLimitMiddleware, RetryMiddleware


def test_retry_middleware_backoff_delay_is_exponential():
    retry = RetryMiddleware(base_delay=1.0, max_retries=3)
    assert retry.backoff_delay(0) == 1.0
    assert retry.backoff_delay(1) == 2.0
    assert retry.backoff_delay(2) == 4.0


def test_retry_middleware_should_retry_on_retryable_status():
    retry = RetryMiddleware(base_delay=0.0, max_retries=2)
    assert retry.should_retry(0, status_code=503) is True
    assert retry.should_retry(0, status_code=404) is False
    assert retry.should_retry(2, status_code=503) is False


def test_retry_middleware_should_retry_on_exception():
    retry = RetryMiddleware(base_delay=0.0, max_retries=2)
    assert retry.should_retry(0, exception=Exception("boom")) is True


def test_rate_limit_middleware_enforces_min_delay():
    rate_limit = RateLimitMiddleware(min_delay=0.05)
    start = time.perf_counter()
    rate_limit.process_request("https://example.com/a", {})
    rate_limit.process_request("https://example.com/b", {})
    elapsed = time.perf_counter() - start
    assert elapsed >= 0.05


def test_rate_limit_middleware_different_domains_not_throttled():
    rate_limit = RateLimitMiddleware(min_delay=1.0)
    start = time.perf_counter()
    rate_limit.process_request("https://example.com/a", {})
    rate_limit.process_request("https://other.com/b", {})
    elapsed = time.perf_counter() - start
    assert elapsed < 0.5


def test_logging_middleware_process_request_and_response():
    logging_mw = LoggingMiddleware()
    url, headers = logging_mw.process_request("https://example.com/", {"User-Agent": "UA"})
    assert url == "https://example.com/"

    class FakeResponse:
        status_code = 200
        url = "https://example.com/"

    result = logging_mw.process_response(FakeResponse())
    assert result.status_code == 200
