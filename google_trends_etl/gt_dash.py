'''
This is the tab for visualisations of the google trends data
'''
import streamlit as st
import pandas as pd
from pytrends.request import TrendReq
from pytrends.exceptions import TooManyRequestsError


class DataManipulator():

    @st.cache_data
    def get_trends_data(_self, topic: str) -> pd.DataFrame:
        '''
        Obtain dataframes to be cached
        '''
        pytrends = TrendReq(hl='en-US', tz=360)

        try:
            pytrends.build_payload(kw_list=[topic], timeframe='today 12-m')
            df_weekly = pytrends.interest_over_time()
            pytrends.build_payload(kw_list=[topic], timeframe='now 7-d')
            df_daily = pytrends.interest_over_time()

        except TooManyRequestsError:
            st.text('Too many requests. Please try again later.')
            empty_df = pd.DataFrame(
                data={'date': [], 'topic_name': [], 'hits': []})
            return empty_df, empty_df

        return _self.prepare_df(df_weekly, topic), _self.prepare_df(df_daily, topic)

    def prepare_df(self, df: pd.DataFrame, topic: str) -> pd.DataFrame:
        '''
        Prepares the dataframes to be used in the visualisations
        '''
        df['topic_name'] = topic
        df['date'] = df.index
        df.rename(columns={topic: 'hits'}, inplace=True)
        df = df[['date', 'hits', 'topic_name']]
        return df

    def initialise_session_state_dataframes(self) -> None:
        '''
        Sets up the dataframes to be added to when the session begins
        '''
        if 'weekly_df' not in st.session_state:
            st.session_state.weekly_df = pd.DataFrame(
                data={'date': [], 'topic_name': [], 'hits': []})
        if 'daily_df' not in st.session_state:
            st.session_state.daily_df = pd.DataFrame(
                data={'date': [], 'topic_name': [], 'hits': []})

    def update_dataframes(self, topic: str) -> None:
        '''
        Updates dataframes with new topic data
        '''
        new_dfs = self.get_trends_data(topic)

        st.session_state.weekly_df = pd.concat([
            st.session_state.weekly_df, new_dfs[0]])
        st.session_state.daily_df = pd.concat([
            st.session_state.daily_df, new_dfs[1]])


class STDisplayer():

    def filter_trend_options(self, df: pd.DataFrame, unique_key: str) -> pd.DataFrame:
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

    def weekly_line_chart(self, df: pd.DataFrame) -> None:
        '''
        Creates a line chart which shows hourly sales for each truck
        '''

        data = self.filter_trend_options(df, unique_key='unique1')

        st.line_chart(data, x='date', x_label='Week Start Date',  y='hits',
                      y_label='Hit Rate', color='topic_name')

    def daily_line_chart(self, df: pd.DataFrame) -> None:
        '''
        Creates a line chart which shows hourly sales for each topic
        '''

        data = self.filter_trend_options(df, unique_key='unique2')

        st.line_chart(data, x='date', x_label='Hour Start Date',  y='hits',
                      y_label='Hit Rate', color='topic_name')

    def topic_input(self) -> str:
        '''
        Takes input as topic
        '''
        topic = st.text_input('Input a Topic to View.')
        return topic


if __name__ == '__main__':
    st.title('Google Search Trends')

    display = STDisplayer()
    manipulator = DataManipulator()

    manipulator.initialise_session_state_dataframes()
    st.text('Please Input a topic to see the relevant search '
            'trends over the last year and the last week.')
    input_topic = display.topic_input()

    if input_topic:

        manipulator.update_dataframes(input_topic)

        display.weekly_line_chart(st.session_state.weekly_df)
        display.daily_line_chart(st.session_state.daily_df)
