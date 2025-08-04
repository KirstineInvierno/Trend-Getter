"""This is the dashboard that will visualise topic trends from bluesky and pytrends"""
import streamlit as st
import re
import logging
from insert_email import EmailInserter
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


def validate_email(email: str) -> bool:
    """Checks if email is a valid input"""
    email_regex = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w+$")
    if email_regex.match(email):
        return True
    else:
        return False


def unsubscribe() -> None:
    """Allows a user to enter their email and unsubscribe to a topic"""
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


if __name__ == "__main__":
    st.title("Trendgetter")

    col1, col2 = st.columns(2)
    with col1:
        st.header("Subscribe")
        subscription()
    with col2:
        st.header("Unsubscribe")
        unsubscribe()
