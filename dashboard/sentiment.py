import streamlit as st
import pandas as pd
import altair as alt
from scipy import ndimage


def sentiment_mentions(df: pd.DataFrame, group: bool = True) -> pd.DataFrame:
    weightings = {
        "NEG": -1,
        "NEU": 1,
        "POS": 1
    }

    df["weighting"] = df["sentiment_label"].map(
        lambda label: weightings[label])

    if group:
        df = df.groupby("topic_name").sum("weighting").reset_index()

    return df


def sentiment_bar(df: pd.DataFrame, topic_df: pd.DataFrame) -> None:

    options = st.multiselect(
        "Select a topic to view the total popularity score of a topic",
        topic_df["topic_name"].unique(),
        default=["technology", "machine learning",
                 "artificial intelligence", "cybersecurity"],
        key=8
    )
    if not options:
        st.info("Please select a topic")
        return
    df = df[df["topic_name"].isin(options)]

    if df.empty:
        st.info(f"No mentions for the selected topic(s)")
        return

    df['topic_name'] = df['topic_name'].str.capitalize()

    source = sentiment_mentions(df)

    bar = alt.Chart(source).mark_bar().encode(
        x=alt.X('topic_name', title="Topic Name",
                axis=alt.Axis(labelAngle=-45)),
        y=alt.Y('weighting', title="Score"),
        color=alt.Color("topic_name", title="Topic Name")
    ).configure(
        background='#EBF7F7'
    ).properties(
        title=alt.Title(text="Popularity Scores", anchor='middle')
    )

    st.altair_chart(bar)


def sentiment_graph(df: pd.DataFrame, topic_df: pd.DataFrame) -> None:
    st.markdown("""
        **What does 'Popularity score' mean?**  
        Popularity score = number of positive mentions - number of negative mentions
        """)
    options = st.multiselect(
        "Select a topic to view the popularity score of that topic per day",
        topic_df["topic_name"].unique(),
        default="technology",
    )
    if not options:
        st.info("Please select a topic")
        return
    df = df[df["topic_name"].isin(options)]

    if df.empty:
        st.info(f"No mentions for the selected topic(s)")
        return

    df['timestamp'] = pd.to_datetime(
        df['timestamp'])

    df = sentiment_mentions(df, False)
    df['topic_name'] = df['topic_name'].str.capitalize()

    df = df.groupby([pd.Grouper(key='timestamp', freq='h'),
                    "topic_name"]).sum("weighting").reset_index()

    df['smoothed_weighting'] = ndimage.gaussian_filter1d(
        df['weighting'], sigma=1.0)

    graph = alt.Chart(df).mark_line().mark_area(
        line={'color': 'darkgreen'},
        color=alt.Gradient(
            gradient='linear',
            stops=[alt.GradientStop(color='white', offset=0),
                   alt.GradientStop(color='darkgreen', offset=1)],
            x1=1,
            x2=1,
            y1=1,
            y2=0
        )
    ).encode(
        x=alt.X('timestamp', title="Time"),
        y=alt.Y('smoothed_weighting', title="Score"),
        color=alt.Color("topic_name", title="Topic Name")
    ).configure(
        background='#EBF7F7'
    ).properties(
        title=alt.Title(text="Popularity Score Over time", anchor='middle')
    )

    st.altair_chart(graph)
