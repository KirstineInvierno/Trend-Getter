import streamlit as st
import re
from insert_phone_number import PhoneNumberInserter


def validate_phone_number(phone_number: str) -> bool:
    """Checks if number is a valid UK phone number"""
    phone_number_regex = re.compile(r'^(?:\+44|0)7\d{9}$')
    if phone_number_regex.match(phone_number):
        return True
    else:
        return False


def phone_number_input() -> None:
    """Takes the phone number as an input and inserts it into the RDS if it is valid and does 
    not already exist in the RDS."""
    with st.form("Phone number form"):
        user_input = st.text_input("Enter phone number:")
        submit = st.form_submit_button("Submit phone number")
        if submit:
            if validate_phone_number(user_input):
                phone_number_inserter = PhoneNumberInserter()
                result = phone_number_inserter.insert_number(user_input)
                if result is True:
                    st.write(f"phone number {user_input} submitted")
                else:
                    st.write(f"phone number {user_input} already exists")
            else:
                st.write(f"{user_input} is not a valid UK phone number")


if __name__ == "__main__":
    st.title("Trendgetter")
    phone_number_input()
