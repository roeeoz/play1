from testbed_utils.reports.category_labels import CATEGORY_LABELS, resolve


def test_known_code_returns_hebrew_label():
    label = resolve("hospitalization")
    assert label == "אשפוז"
    assert len(label) > 0


def test_specialist_visit():
    assert resolve("specialist_visit") == "ביקור מומחה"


def test_dental():
    assert resolve("dental") == "טיפול שיניים"


def test_optical():
    assert resolve("optical") == "אופטיקה"


def test_medications():
    assert resolve("medications") == "תרופות"


def test_emergency():
    assert resolve("emergency") == "חדר מיון"


def test_surgery():
    assert resolve("surgery") == "ניתוח"


def test_physiotherapy():
    assert resolve("physiotherapy") == "פיזיותרפיה"


def test_unknown_code_returns_input():
    unknown = "some_unknown_code"
    assert resolve(unknown) == unknown


def test_unknown_code_not_none():
    result = resolve("nonexistent_category")
    assert result is not None
    assert isinstance(result, str)


def test_all_dict_values_are_nonempty_strings():
    for key, value in CATEGORY_LABELS.items():
        assert isinstance(value, str), f"Value for {key!r} is not a string"
        assert len(value) > 0, f"Value for {key!r} is empty"


def test_dict_has_at_least_8_entries():
    assert len(CATEGORY_LABELS) >= 8
