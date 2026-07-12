import pytest

from testbed_utils.numutils import clamp


class TestClamp:
    def test_within_range(self):
        assert clamp(5, 1, 10) == 5

    def test_below_lo(self):
        assert clamp(-3, 0, 100) == 0

    def test_above_hi(self):
        assert clamp(200, 0, 100) == 100

    def test_at_lo_boundary(self):
        assert clamp(0, 0, 10) == 0

    def test_at_hi_boundary(self):
        assert clamp(10, 0, 10) == 10

    def test_lo_equals_hi(self):
        assert clamp(5, 7, 7) == 7

    def test_floats(self):
        assert clamp(1.5, 1.0, 2.0) == 1.5

    def test_invalid_dimensions_raises(self):
        with pytest.raises(ValueError):
            clamp(5, 10, 1)
