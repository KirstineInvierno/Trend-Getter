import streamlit as st
import re
from insert_phone_number import PhoneNumberInserter
from insert_topic import TopicInserter
from insert_subscription import SubscriptionInserter


def validate_phone_number(phone_number: str) -> bool:
    """Checks if number is a valid UK phone number"""
    phone_number_regex = re.compile(r'^(?:\+44|0)7\d{9}$')
    if phone_number_regex.match(phone_number):
        return True
    else:
        return False


def subscription() -> None:
    """Takes a phone number and a topic and subscribes the user to the topic if they 
    are not already subscribed."""
    with st.form("Subscribe form"):
        phone_input = st.text_input("Enter phone number:")
        topic_input = st.text_input("Subscribe to a topic:")
        submit = st.form_submit_button("Submit")
        if submit:
            if validate_phone_number(phone_input):
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

            else:
                st.error(
                    f"{phone_input} is not a valid UK phone number")


if __name__ == "__main__":
    st.title("Trendgetter")
    subscription()
