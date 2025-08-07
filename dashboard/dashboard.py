"""This is the dashboard that will visualise topic trends from bluesky and pytrends"""
import streamlit as st
import re
import logging
from insert_topic import TopicInserter, Connection
from insert_email import EmailInserter
from insert_topic import TopicInserter
from insert_subscription import SubscriptionInserter
from sentiment import sentiment_graph, sentiment_pie, sentiment_bar
import gt_dash
import pandas as pd
import altair as alt
logging.basicConfig(
    format="%(levelname)s | %(asctime)s | %(message)s", level=logging.INFO)


class RDSLoadError(Exception):
    """Exception raised when loading from an RDS failes"""
    pass


@st.cache_data(ttl="300s")
def load_mentions():
    connection = Connection()
    conn = connection.get_connection()
    query = """
            SELECT mention_id,topic_name,timestamp,sentiment_label, sentiment_score FROM bluesky.mention
            join bluesky.topic using(topic_id);
        """

    try:
        with connection.get_connection() as conn:
            df = pd.read_sql(query, conn)
        return df

    except Exception as e:
        logging.error("loading of mentions failed: %s", e)
        raise RDSLoadError("loading of mentions failed") from e


@st.cache_data(ttl="300s")
def load_topics():
    connection = Connection()
    conn = connection.get_connection()
    query = """
           SELECT topic_name FROM  bluesky.topic;
       """
    try:
        with connection.get_connection() as conn:
            df = pd.read_sql(query, conn)
        return df

    except Exception as e:
        logging.error("loading of topics failed: %s", e)
        raise RDSLoadError("loading of topics failed") from e


def validate_phone_number(phone_number: str) -> bool:
    """Checks if number is a valid UK phone number"""
    phone_number_regex = re.compile(r'^(?:\+44|0)7\d{9}$')
    if phone_number_regex.match(phone_number):
        return True
    else:
        return False


def validate_email(email: str) -> bool:
    """Checks if email is a valid input"""
    email_regex = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w+$")
    if email_regex.match(email):
        return True
    else:
        return False


def unsubscribe() -> None:
    """Allows a user to enter their email and unsubscribe to a topic"""
    st.markdown("""
        **Unsubscribe to a topic**  
       - Unsubscribe from a topic to stop receiving notifications in cases of activity spikes for that topic
        """)
    email_input = st.text_input("Enter your email to manage subscriptions:")
    if email_input:
        if validate_email(email_input):

            try:
                email_inserter = EmailInserter()
                user_id = email_inserter.get_user_id(email_input)
                if user_id == -1:
                    st.error("Email not found")
                    logging.error(
                        f"User tried to unsubscribe with unknown email")
                    return
                subscription_inserter = SubscriptionInserter()
                subscribed_topics = subscription_inserter.get_subscriptions(
                    user_id)
                if subscribed_topics:
                    unsubscribed_topic = st.selectbox(
                        "Select topic to unsubscribe from:", subscribed_topics)
                    if st.button("unsubscribe"):
                        removed = subscription_inserter.unsubscribe(
                            user_id, unsubscribed_topic)
                        if removed:
                            st.success(
                                f"You have unsubscribed from {unsubscribed_topic}")
                        else:
                            st.error(
                                f"Unsubscription from {unsubscribed_topic} failed.")
                else:
                    st.info("You are not subscribed to anything")
            except Exception as e:
                st.error(
                    f"An error occured while managing your subscription:{e}")
            logging.error(f"Unexpected error when unsubscribing.")
        else:
            st.error(
                f"{email_input} is not a valid email")


def subscription() -> None:
    """Takes an email, topic and a threshold, and subscribes the user to the topic if they
    are not already subscribed. If the user is already subscribed, the threshold is updated."""
    st.markdown("""
        **Subscribe to a topic**  
       - Subscribe to a topic to be emailed when there are activity spikes for the chosen topic
       - If the topic does not exist, BlueSky will start tracking the topic for mentions.
       - You can enter a topic you are already subscribed to and change the threshold of mentions
        """)
    with st.form("Subscribe form"):
        email_input = st.text_input("Enter your email:")
        topic_input = st.text_input("Subscribe to a topic:")
        threshold_input = st.text_input(
            "Enter the minimum number of mentions in 10 minutes to trigger a notification:")
        submit = st.form_submit_button("Submit")
        if submit:
            if not validate_email(email_input):
                st.error(
                    f"{email_input} is not a valid email")
                return
            if not threshold_input.isdigit():
                st.error("Threshold must be a whole number")
                return

            try:
                email_inserter = EmailInserter()
                user_id = email_inserter.insert_email(email_input)

                topic_inserter = TopicInserter()
                topic_id = topic_inserter.insert_topic(topic_input)
                subscription_inserter = SubscriptionInserter()
                added = subscription_inserter.insert_subscription(
                    user_id, topic_id, int(threshold_input))
                if added:
                    st.success(
                        f"{email_input} has subscribed to {topic_input} and will be notified when there are more than {threshold_input} mentions in a 10 minute interval")
                else:
                    st.info(
                        f"{email_input} is already subscribed to  {topic_input}. Threshold set to {threshold_input}")
            except Exception as e:
                st.error(
                    f"An error occured while subscribing to a topic: {e}")
                logging.error(
                    f"An error occured while subscribing to a topic: {e}.")


def topic_trends(df: pd.DataFrame, topic_df: pd.DataFrame) -> None:
    """Loads an altair line chart that shows trends of a topic per day """
    st.markdown("""
        **Bluesky topic trends** 
                
        This is a live dashboard that tracks topic mentions on bluesky in realtime.
        - View the trends of chosen topic(s) across multiple days 
        - View the trends of chosen topic(s) on a specific day
        """)
    options = st.multiselect(
        "Select a topic to view the number of mentions of that topic per day",
        topic_df["topic_name"].unique(),
        default="art",
        key=5
    )
    if not options:
        st.info("Please select a topic")
        return

    df = df[df["topic_name"].isin(options)].copy()
    df['timestamp'] = pd.to_datetime(
        df['timestamp'])

    df = df.groupby([pd.Grouper(key='timestamp', freq='D'),
                    "topic_name"]).size().reset_index(name='mentions')

    if df.empty:
        st.info(f"No mentions for the selected topic(s)")

    line_chart = alt.Chart(df).mark_line(point=True).encode(
        x=alt.X('timestamp:T', axis=alt.Axis(format="%b %d"), title="Date"),
        y=alt.Y('mentions:Q', title='Total mentions'),
        color=alt.Color('topic_name:N', title="Topic"),
        tooltip=["timestamp", "mentions", "topic_name"]).configure(
        background='#EBF7F7'
    ).properties(title='Mentions by topic per day')

    st.altair_chart(line_chart)


def topic_trends_by_hour(df: pd.DataFrame, topic_df: pd.DataFrame) -> None:
    """Displays an hourly line chart for mentions by topic on a selected day."""

    options = st.multiselect(
        "Select a topic to view the number of mentions of that topic by hour on a selected day",
        topic_df["topic_name"].unique(),
        default="art",
        key=6,
    )

    if not options:
        st.info("Please select a topic")
        return
    df = df[df["topic_name"].isin(options)].copy()
    dates = pd.to_datetime(df["timestamp"]).dt.date.unique()
    selected_date = st.date_input(
        "Select a date to view the trend of a topic",
        min_value=min(dates),
        max_value=max(dates)
    )

    df["timestamp"] = pd.to_datetime(df["timestamp"])

    df = df[df["timestamp"].dt.date == selected_date]

    df["hour"] = df["timestamp"].dt.hour
    df = df.groupby(["hour", "topic_name"]).size().reset_index(name="mentions")

    if df.empty:
        st.info(f"No mentions for the selected topic(s) on {selected_date}")
        return

    chart = alt.Chart(df).mark_line(point=True).encode(
        x=alt.X("hour:Q", axis=alt.Axis(title="Hour of Day")),
        y=alt.Y("mentions:Q", axis=alt.Axis(title="Mentions")),
        color=alt.Color("topic_name:N", title="Topic"),
        tooltip=["hour", "mentions", "topic_name"]
    ).configure(
        background='#EBF7F7'
    ).properties(title=f"Hourly Mentions on {selected_date}")

    st.altair_chart(chart, use_container_width=True)


def topic_sentiment_pie_chart(df: pd.DataFrame, topic_df: pd.DataFrame):
    st.markdown("""
        **View the sentiment of topic(s)**  
           The sentiment of a topic is the public opinion towards a topic and is calculated using an AI model.
        """)
    options = st.multiselect(
        "Select a topic to view the sentiment of its mentions.",
        topic_df["topic_name"].unique(),
        default=None,
        key=7,
    )

    if not options:
        st.info("Please select a topic")
        return

    df = df[df["topic_name"].isin(options)].copy()
    topic_names = df["topic_name"].unique()
    title = ", ".join(topic_names)
    sentiment_df = df["sentiment_label"].value_counts().reset_index()
    sentiment_df.columns = ["sentiment of topic(s)", "mention count"]
    sentiment_df["sentiment of topic(s)"] = sentiment_df["sentiment of topic(s)"].replace(
        {"POS": "Positive", "NEG": "Negative", "NEU": "Neutral"})
    colours = alt.Scale(domain=["Negative", "Positive", "Neutral"],
                        range=["#bb3131", "#009e69", "#eeece1"])
    pie_chart = alt.Chart(sentiment_df).mark_arc(stroke="black", strokeWidth=0.5).encode(
        theta=alt.Theta("mention count:Q"),
        color=alt.Color("sentiment of topic(s):N", scale=colours),
        tooltip=["sentiment of topic(s)", "mention count"]
    ).configure(
        background='#EBF7F7'
    ).properties(title=f"Public sentiment for {title}")
    st.altair_chart(pie_chart, use_container_width=True)


if __name__ == "__main__":
    st.markdown(
        """
   <style>
   .stApp {
       background-color: #E1FAF9;
   }
   </style>
   """,
        unsafe_allow_html=True
    )

    st.image("../images/trendgetter_transparrent.png")
    df = load_mentions()
    topic_df = load_topics()

    tab1, tab2 = st.tabs(["Bluesky Dashboard", "Google Trends Dashboard"])
    with tab1:
        st.markdown(
            "<h1>Bluesky <span style='color: #009e69;'>Trends</span></h1>",
            unsafe_allow_html=True
        )

        dash_tab, sub_tab, unsub_tab = st.tabs(
            ["Dashboard", "Subscribe", "Unsubscribe"])
        with dash_tab:
            topic_trends(df, topic_df)
            st.markdown("---")
            topic_trends_by_hour(df, topic_df)
            st.markdown("---")
            topic_sentiment_pie_chart(df, topic_df)
            st.markdown("---")
            sentiment_graph(df, topic_df)
            st.markdown("---")
            sentiment_bar(df)

        with sub_tab:
            subscription()
        with unsub_tab:
            unsubscribe()

    with tab2:
        gt_dash.gt_dashboard()
