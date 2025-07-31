import datetime
import streamlit as st
import pandas as pd
from pytrends.request import TrendReq

if 'input' not in st.session_state:
    st.session_state.input = 'trump'


@st.cache_data
def get_trends_data(topic=st.session_state.input) -> pd.DataFrame:
    pytrends = TrendReq(hl='en-US', tz=360)

    pytrends.build_payload(kw_list=[topic], timeframe='today 12-m')
    df_weekly = pytrends.interest_over_time()
    pytrends.build_payload(kw_list=[topic], timeframe='now 7-d')
    df_daily = pytrends.interest_over_time()
    df_daily['topic_name'] = topic
    df_weekly['topic_name'] = topic
    st.text(df_daily.columns)
    df_daily['date'] = df_daily.index
    df_weekly['date'] = df_weekly.index
    df_daily.rename(columns={topic: 'hits'}, inplace=True)
    df_weekly.rename(columns={topic: 'hits'}, inplace=True)
    df_daily = df_daily[['date', 'hits', 'topic_name']]
    df_weekly = df_weekly[['date', 'hits', 'topic_name']]
    return df_weekly, df_daily


def filter_trend_options(df: pd.DataFrame, unique_key: str) -> pd.DataFrame:
    '''
    Filters data frame based on dashboard user's input
    '''
    options = st.multiselect(
        'Which Trends?',
        df['topic_name'].unique(),
        default=df["topic_name"].unique(),
        key=unique_key
    )

    data = df[df["topic_name"].isin(options)]
    return data


def weekly_line_chart(df: pd.DataFrame):
    '''
    Creates a line chart which shows hourly sales for each truck
    '''

    data = filter_trend_options(df, unique_key='topic')

    st.line_chart(data, x='date', x_label='Week Start Date',  y='hits',
                  y_label='Hit Rate', color='topic_name')


def daily_line_chart(df: pd.DataFrame):
    '''
    Creates a line chart which shows hourly sales for each topic
    '''

    data = filter_trend_options(df, unique_key='topic2')

    st.line_chart(data, x='date', x_label='Hour Start Date',  y='hits',
                  y_label='Hits Rate', color='topic_name')


def topic_input():
    '''
    Takes input as topic
    '''
    input_topic = st.text_input('Input a Topic to View')
    return input_topic


def increment_counter():
    st.session_state.count += 1


@st.cache_data
def concat_dfs(df1, df2):
    return pd.concat(df1, df2)


if __name__ == '__main__':
    if 'weekly_df' not in st.session_state:
        st.session_state.weekly_df = pd.DataFrame(
            data={'date': [1], 'topic_name': [1], 'hits': [1]})
    if 'count' not in st.session_state:
        st.session_state.count = 0
    st.text(st.session_state.count)
    if st.session_state.count == 0:
        weekly_df = pd.DataFrame(
            data={'date': [1], 'topic_name': [1], 'hits': [1]})
        daily_df = pd.DataFrame(
            data={'date': [2], 'topic_name': [2], 'hits': [2]})
        increment_counter()
    st.text(st.session_state.count)
    topic = st.text_input(
        'Input a Topic to View')
    # st.dataframe(daily_df)
    st.dataframe(st.session_state.weekly_df)

    if topic:
        # dfs = get_trends_data()
        st.session_state.weekly_df = pd.concat([
            st.session_state.weekly_df, st.session_state.weekly_df])

        st.dataframe(st.session_state.weekly_df)
        # st.dataframe(daily_df)
        weekly_line_chart(st.session_state.weekly_df)
        # daily_line_chart(daily_df)
        st.text(st.session_state.count)
