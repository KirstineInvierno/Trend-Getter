"""This is the tab for visualisations of the google trends data"""
import streamlit as st
import pandas as pd
from pytrends.request import TrendReq
from pytrends.exceptions import TooManyRequestsError


class DataManipulator():

    @st.cache_data
    def get_trends_data(_self, topic: str, timeframe: str) -> pd.DataFrame:
        """Obtain dataframes to be cached"""
        pytrends = TrendReq(hl='en-GB', tz=60)

        try:
            pytrends.build_payload(kw_list=[topic], timeframe=timeframe)
            df = pytrends.interest_over_time()

        except TooManyRequestsError:
            st.text('Too many requests. Please try again later.')
            empty_df = pd.DataFrame(
                data={'date': [], 'topic_name': [], 'hits': []})
            return empty_df

        return _self.prepare_df(df, topic)

    def prepare_df(self, df: pd.DataFrame, topic: str) -> pd.DataFrame:
        """Prepares the dataframes to be used in the visualisations"""
        df['topic_name'] = topic
        df['date'] = df.index
        df.rename(columns={topic: 'hits'}, inplace=True)
        df = df[['date', 'hits', 'topic_name']]
        return df

    def initialise_session_state_dataframes(self) -> None:
        """Sets up the dataframes to be added to when the session begins"""
        if 'trend_df' not in st.session_state:
            st.session_state.trend_df = pd.DataFrame(
                data={'date': [], 'topic_name': [], 'hits': []})

    def update_dataframes(self, topic: str, timeframe: str) -> None:
        """Updates dataframes with new topic data"""
        new_df = self.get_trends_data(topic, timeframe)

        st.session_state.trend_df = pd.concat([
            st.session_state.trend_df, new_df])


class STDisplayer():

    def filter_trend_options(self, df: pd.DataFrame, unique_key: str) -> pd.DataFrame:
        """Filters data frame based on dashboard user's input"""
        options = st.multiselect(
            'Which Trends?',
            df['topic_name'].unique(),
            default=df["topic_name"].unique(),
            key=unique_key
        )

        data = df[df["topic_name"].isin(options)]
        return data

    def trend_line_chart(self, df: pd.DataFrame) -> None:
        """Creates a line chart which shows the popularity of a topic over a certain timeframe"""

        data = self.filter_trend_options(df, unique_key='trend_chart')

        st.line_chart(data, x='date', x_label='date',  y='hits',
                      y_label='Hit Rate', color='topic_name')

    def topic_input(self) -> str:
        """Takes input as topic"""
        topic = st.text_input('Input a Topic to View.')
        return topic


if __name__ == '__main__':
    st.title('Google Search Trends')
    st.markdown("""
        **What does 'Hit rate' mean?**  
        This is a relative score provided by Google Trends.  
        - 100 = peak popularity  
        - 50 = moderate interest  
        - 0 = No interest 
        """)

    display = STDisplayer()
    manipulator = DataManipulator()

    manipulator.initialise_session_state_dataframes()
    st.text('Please Input a topic to see the relevant search '
            'trends over the last year and the last week.')
    timeframe_options = {
        'Last 7 days': 'now 7-d',
        'Last 1 month': 'today 1-m',
        'Last 12 months': 'today 12-m',
    }

    timeframe_label = st.selectbox(
        'Select a timeframe to view topic popularity',
        list(timeframe_options.keys())
    )
    timeframe = timeframe_options[timeframe_label]

    with st.form("trend_form"):
        input_topic = display.topic_input()
        submitted = st.form_submit_button("Submit")

    if input_topic and submitted:

        manipulator.update_dataframes(input_topic, timeframe)

        display.trend_line_chart(st.session_state.trend_df)
