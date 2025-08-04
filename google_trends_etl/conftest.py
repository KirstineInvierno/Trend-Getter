# pylint: skip-file
import pytest
import pandas as pd
from gt_dash import DataManipulator


@pytest.fixture
def unprepared_df():
    df = pd.DataFrame(
        data={'date': ["1/1/2020 10:00:00+00:00", "2/1/2020 11:00:00+00:00"],
              'thing': [35, 67]})
    df.set_index('date', inplace=True)
    return df


@pytest.fixture
def unprepared_df_two():
    df = pd.DataFrame(
        data={'date': ["1/1/2020 10:00:00+00:00", "2/1/2020 11:00:00+00:00"],
              'thing2': [34, 66]})
    df.set_index('date', inplace=True)
    return df


@pytest.fixture
def prepared_df():
    df = pd.DataFrame({
        'date': pd.date_range("2025-01-01", periods=2),
        'hits': [23, 54],
        'topic_name': ['topic_1', 'topic_2']
    })
    return df


@pytest.fixture
def manipulator_instance():
    return DataManipulator()
