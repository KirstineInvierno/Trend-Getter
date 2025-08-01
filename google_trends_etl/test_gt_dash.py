import pandas as pd
import pytest
import streamlit as st
from gt_dash import DataManipulator, STDisplayer


@pytest.fixture
def unprepared_df():
    """example unprepared DataFrame"""
    df = pd.DataFrame(
        data={'date': ["1/1/2020 10:00:00+00:00", "2/1/2020 11:00:00+00:00"],
              'thing': [35, 67]})
    df.set_index('date', inplace=True)
    return df


@pytest.fixture
def unprepared_df_two():
    """example unprepared DataFrame"""
    df = pd.DataFrame(
        data={'date': ["1/1/2020 10:00:00+00:00", "2/1/2020 11:00:00+00:00"],
              'thing2': [34, 66]})
    df.set_index('date', inplace=True)
    return df


@pytest.fixture
def manipulator_instance() -> DataManipulator:
    '''Gets an instance of the manipulator to use in tests'''
    return DataManipulator()


def test_prepare_df_columns(unprepared_df, manipulator_instance):
    '''
    Checks prepared dataframe has correct columns
    '''

    prepared_df: pd.DataFrame = manipulator_instance.prepare_df(
        df=unprepared_df, topic='thing')

    cols = prepared_df.columns

    assert len(cols) == 3
    assert 'date' in cols
    assert 'topic_name' in cols
    assert 'hits' in cols


def test_prepare_df_topic_col(unprepared_df, manipulator_instance):
    '''
    Checks prepared dataframe has correct values in topic_name
    '''

    prepared_df: pd.DataFrame = manipulator_instance.prepare_df(
        unprepared_df, 'thing')

    assert prepared_df['topic_name'].iloc[0] == 'thing'
    assert prepared_df['topic_name'].iloc[1] == 'thing'

# test concat
