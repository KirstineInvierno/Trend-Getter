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
        "Select a topic to view the popularity score of that topic per day",
        topic_df["topic_name"].unique(),
        key=8
    )
    if not options:
        st.info("Please select a topic")
        return
    df = df[df["topic_name"].isin(options)]

    if df.empty:
        st.info(f"No mentions for the selected topic(s)")
        return

    source = sentiment_mentions(df)

    bar = alt.Chart(source).mark_bar().encode(
        x=alt.X('topic_name', title="Topic Name"),
        y=alt.Y('weighting', title="Score")
    ).configure(
        background='#EBF7F7'
    ).properties(
        title=f"Popularity Scores"
    )

    st.altair_chart(bar)


def sentiment_graph(df: pd.DataFrame, topic_df: pd.DataFrame) -> None:
    options = st.multiselect(
        "Select a topic to view the popularity score of that topic per day",
        topic_df["topic_name"].unique()
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
        title=f"Popularity Score Over time"
    )

    st.altair_chart(graph)


def sentiment_pie(mentions_df: pd.DataFrame) -> None:
    sentiment_dict = {
        "NEG": "Negative",
        "NEU": "Neutral",
        "POS": "Positive"
    }

    colours = ["#a83232", "#575c60", "#32a852"]

    source = mentions_df.groupby("sentiment_label").count().reset_index()
    source["Sentiment"] = source["sentiment_label"].map(
        lambda label: sentiment_dict[label])
    print(source.info())

    pie = alt.Chart(source).mark_arc().encode(
        theta="mention_id",
        color="Sentiment"
    ).configure(
        background='#EBF7F7'
    ).properties(
        title=f"Sentiment pie"
    ).configure_range(
        category=alt.RangeScheme(colours)
    )

    st.altair_chart(pie)
