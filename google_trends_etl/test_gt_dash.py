import pandas as pd
import streamlit as st
from unittest.mock import patch


def test_prepare_df_columns(unprepared_df, manipulator_instance):
    """Checks prepared dataframe has correct columns"""

    prepared_df: pd.DataFrame = manipulator_instance.prepare_df(
        df=unprepared_df, topic='thing')

    cols = prepared_df.columns

    assert len(cols) == 3
    assert 'date' in cols
    assert 'topic_name' in cols
    assert 'hits' in cols


def test_prepare_df_topic_col(unprepared_df, manipulator_instance):
    """Checks prepared dataframe has correct values in topic_name"""

    prepared_df: pd.DataFrame = manipulator_instance.prepare_df(
        unprepared_df, 'thing')

    assert prepared_df['topic_name'].iloc[0] == 'thing'
    assert prepared_df['topic_name'].iloc[1] == 'thing'


def test_update_dataframe(prepared_df, manipulator_instance):
    """Checks prepared dataframe is correctly updated"""

    st.session_state.trend_df = pd.DataFrame(
        columns=['date', 'hits', 'topic_name'])

    with patch.object(manipulator_instance, 'get_trends_data', return_value=prepared_df):
        manipulator_instance.update_dataframes("topic_1", "today 12-m")
    result = st.session_state.trend_df
    assert len(result) == 2
    assert "topic_1" in result['topic_name'].values
    assert "topic_2" in result['topic_name'].values
