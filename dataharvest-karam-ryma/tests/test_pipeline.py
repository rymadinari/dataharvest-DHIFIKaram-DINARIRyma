from dataharvest.pipeline import GenericPipeline, PaginationPipeline

SAMPLE_HTML = """
<html><body>
  <div class="quote">
    <h2 class="title"><a href="/item/1">Titre un</a></h2>
  </div>
  <div class="quote">
    <h2 class="title"><a href="/item/2">Titre deux</a></h2>
  </div>
</body></html>
"""

SELECTORS = {"titre": "h2.title a", "url": "h2.title a"}


def test_process_returns_list_always():
    pipeline = GenericPipeline(SELECTORS)
    result = pipeline.process("")
    assert result == []
    assert isinstance(result, list)


def test_process_does_not_raise_on_missing_selector():
    pipeline = GenericPipeline({"titre": "h2.title a", "inexistant": ".ne-matche-rien"})
    items = pipeline.process(SAMPLE_HTML)
    assert len(items) == 2
    assert items[0]["inexistant"] == ""


def test_process_extracts_expected_fields():
    pipeline = GenericPipeline(SELECTORS, base_url="https://example.com")
    items = pipeline.process(SAMPLE_HTML)

    assert len(items) == 2
    assert items[0]["titre"] == "Titre un"
    assert items[0]["url"] == "https://example.com/item/1"
    assert items[1]["titre"] == "Titre deux"


class FakePaginationConfig:
    pattern = "/page/{n}/"
    start = 1
    max_pages = 2


def test_next_page_url_returns_none_when_no_items():
    pipeline = PaginationPipeline(SELECTORS, FakePaginationConfig())
    assert pipeline.next_page_url("<html></html>", "https://example.com/page/1/") is None


def test_next_page_url_returns_none_at_max_pages():
    pipeline = PaginationPipeline(SELECTORS, FakePaginationConfig())
    next_url = pipeline.next_page_url(SAMPLE_HTML, "https://example.com/page/2/")
    assert next_url is None


def test_next_page_url_builds_correct_next_page():
    pipeline = PaginationPipeline(SELECTORS, FakePaginationConfig())
    next_url = pipeline.next_page_url(SAMPLE_HTML, "https://example.com/page/1/")
    assert next_url == "https://example.com/page/2/"
