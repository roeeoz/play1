from guestbook.greeting import shout


def test_shout_lowercase_name():
    assert shout("ada") == "HELLO, ADA!"


def test_shout_mixed_case_name():
    assert shout("Ada") == "HELLO, ADA!"


def test_shout_empty_name():
    assert shout("") == "HELLO, !"
