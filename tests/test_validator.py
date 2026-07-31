from dataharvest.validator import Validator


def test_validate_rejects_items_missing_required_field():
    validator = Validator(required_fields=["titre", "url"])
    items = [
        {"titre": "OK", "url": "https://example.com/1"},
        {"titre": "", "url": "https://example.com/2"},
        {"url": "https://example.com/3"},
    ]
    valid, rejected = validator.validate(items)
    assert len(valid) == 1
    assert len(rejected) == 2


def test_validate_rejects_items_with_invalid_url():
    validator = Validator(required_fields=["titre", "url"])
    items = [
        {"titre": "OK", "url": "https://example.com/1"},
        {"titre": "Bad", "url": "not-a-url"},
        {"titre": "Bad2", "url": "ftp://example.com"},
    ]
    valid, rejected = validator.validate(items)
    assert len(valid) == 1
    assert len(rejected) == 2


def test_validate_rejects_items_below_min_length():
    validator = Validator(required_fields=["titre"], min_lengths={"titre": 5})
    items = [{"titre": "abcdef"}, {"titre": "ab"}]
    valid, rejected = validator.validate(items)
    assert len(valid) == 1
    assert len(rejected) == 1


def test_is_valid_url():
    validator = Validator(required_fields=[])
    assert validator.is_valid_url("https://example.com/page") is True
    assert validator.is_valid_url("http://example.com") is True
    assert validator.is_valid_url("example.com") is False
    assert validator.is_valid_url("") is False
    assert validator.is_valid_url(None) is False
