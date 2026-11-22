"""QA-20261122-S4: a deliberately failing test on the QA base branch (pre-existing failure)."""


def test_pre_existing_failure_on_the_qa_base():
    assert 1 == 2, "pre-existing failure on the QA base"
