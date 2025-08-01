"""This is the dashboard that will visualise topic trends from bluesky and pytrends"""
import streamlit as st
import re
import logging
from insert_phone_number import PhoneNumberInserter
from insert_topic import TopicInserter
from insert_subscription import SubscriptionInserter

logging.basicConfig(
    format="%(levelname)s | %(asctime)s | %(message)s", level=logging.INFO)


def validate_phone_number(phone_number: str) -> bool:
    """Checks if number is a valid UK phone number"""
    phone_number_regex = re.compile(r'^(?:\+44|0)7\d{9}$')
    if phone_number_regex.match(phone_number):
        return True
    else:
        return False


def unsubscribe() -> None:
    """Allows a user to enter their phone number and unsubscribe to a topic"""
    phone_input = st.text_input("Enter phone number to manage subscriptions:")
    if phone_input:
        if validate_phone_number(phone_input):

            try:
                phone_number_inserter = PhoneNumberInserter()
                user_id = phone_number_inserter.get_user_id(phone_input)
                if user_id == -1:
                    st.error("Phone number not found")
                    logging.error(
                        f"User tried to unsubscribe with unknown phone number")
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
                f"{phone_input} is not a valid UK phone number")


def subscription() -> None:
    """Takes a phone number and a topic and subscribes the user to the topic if they
    are not already subscribed."""
    with st.form("Subscribe form"):
        phone_input = st.text_input("Enter phone number:")
        topic_input = st.text_input("Subscribe to a topic:")
        submit = st.form_submit_button("Submit")
        if submit:
            if validate_phone_number(phone_input):
                try:
                    phone_number_inserter = PhoneNumberInserter()
                    user_id = phone_number_inserter.insert_number(phone_input)

                    topic_inserter = TopicInserter()
                    topic_id = topic_inserter.insert_topic(topic_input)
                    subscription_inserter = SubscriptionInserter()
                    added = subscription_inserter.insert_subscription(
                        user_id, topic_id)
                    if added:
                        st.success(
                            f"{phone_input} has subscribed to {topic_input}")
                    else:
                        st.info(
                            f"{phone_input} is already subscribed to  {topic_input}")
                except Exception as e:
                    st.error(
                        f"An error occured while subscribing to a topic.")
                    logging.error(
                        f"An error occured while subscribing to a topic: {e}.")

            else:
                st.error(
                    f"{phone_input} is not a valid UK phone number")


if __name__ == "__main__":
    st.title("Trendgetter")

    col1, col2 = st.columns(2)
    with col1:
        st.header("Subscribe")
        subscription()
    with col2:
        st.header("Unsubscribe")
        unsubscribe()
