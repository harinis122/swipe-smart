"""
Front-end UI to gain user input about meal swipes
"""

import streamlit as st
from datetime import date
import math
import time


def user_input():
    # Quarter selection
    quarter = st.selectbox(
        "What quarter is it?",
        ['Fall', 'Winter', 'Spring']
    )

    # Swipe input
    swipes = st.number_input(
        "How many meal swipes do you have left?",
        min_value=0,
        step=1
    )

    # Days on campus
    st.subheader("What days will you be on campus to use your meal plans?")

    days = {
        "Monday": st.checkbox("Monday"),
        "Tuesday": st.checkbox("Tuesday"),
        "Wednesday": st.checkbox("Wednesday"),
        "Thursday": st.checkbox("Thursday"),
        "Friday": st.checkbox("Friday"),
        "Saturday": st.checkbox("Saturday"),
        "Sunday": st.checkbox("Sunday")
    }

    selected_days = [day for day, checked in days.items() if checked]

    # Distribution choice
    st.markdown("### How would you like to distribute your swipes?")
    distribution = st.radio(
        "",
        ["Evenly throughout the quarter",
            "Unevenly (I'll choose how to distribute it)"
        ]
    )

    excluded_weeks = []

    # Show uneven weeks IMMEDIATELY
    if distribution == "Unevenly (I'll choose how to distribute it)":

        end_fall = date(2025, 12, 12)
        end_winter = date(2026, 3, 20)
        end_spring = date(2026, 6, 12)

        if quarter == "Fall":
            end = end_fall
        elif quarter == "Winter":
            end = end_winter
        else:
            end = end_spring

        today = date.today()
        diff_days = (end - today).days
        diff_weeks = max(0, math.floor(diff_days / 7))

        st.subheader("Select the remaining weeks you're NOT using meal swipes")

        for week in range(1, diff_weeks + 1):
            if st.checkbox(f"Week {week}", key=f"week_{week}"):
                excluded_weeks.append(f"Week {week}")

    # Preferences
    like_pref = st.text_input("Describe your food preferences")
    dislike_pref = st.text_input("Describe your dislikes")

    # Submit button
    submitted = st.button("Calculate Swipes!")

    if submitted:
        with st.spinner("Calculating your optimal swipe plan..."):
            time.sleep(2)
            st.success("Plan ready!")
            st.balloons()

        # Swipe calculations
        user_data = {
            "quarter": quarter,
            "swipes": swipes,
            "selected_days": selected_days,
            "distribution": distribution,
            "excluded_weeks": excluded_weeks
        }

        # Preferences
        preference_data = {
            "likes": like_pref,
            "dislikes": dislike_pref
        }

        return user_data, preference_data

    return None, None


def main():
    st.title("Meal Swipe Manager")
    st.write("Helping you plan your meal swipes efficiently!")

    user_data, preference_data = user_input()

    # TODO: delete this later?
    if user_data and preference_data:
        st.success("Data successfully collected!")

        st.write("Swipe Data:", user_data)
        st.write("Preference Data:", preference_data)



if __name__ == "__main__":
    main()
