from datetime import datetime
import pytest
from threshold_check import DataGetter


class TestTCheck:

    def test_get_now(self):
        getter = DataGetter()
        assert isinstance(getter.get_now(), datetime)
