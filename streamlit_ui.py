"""
Front-end UI to gain user input about meal swipes
"""

import streamlit as st
import pandas as pd
from datetime import date
import math
import time
import meal_distribution
import os


def user_input():
    # Quarter selection
    st.subheader("📆 What quarter is it?")
    quarter = st.selectbox(
        "",
        ['Fall', 'Winter', 'Spring']
    )

    # Swipe input
    st.subheader("#️⃣ How many meal swipes do you have left?")
    swipes = st.number_input(
        "",
        min_value=0,
        step=1
    )

    # Days on campus
    st.subheader("☀️ What days will you be on campus to use your meal plans?")

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
    st.subheader("🧮 How would you like to distribute your swipes?")
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

        #today = date.today()
        #diff_days = (end - today).days
        #diff_weeks = max(0, math.ceil(diff_days / 7))
        #total_weeks = 11
        #diff_weeks = min(diff_weeks, total_weeks)
        #start_week = total_weeks - diff_weeks + 1

        diff_weeks = meal_distribution.get_weeks(quarter)
        total_weeks = 11
        start_week = total_weeks - diff_weeks + 1

        st.subheader("❌ Select the remaining weeks you're NOT using meal swipes")

        for week in range(start_week, total_weeks + 1):
            if week == 11:
                label = "Finals Week"
            else:
                label = f"Week {week}"

            if st.checkbox(label, key=f"week_{week}"):
                excluded_weeks.append(f"Week {week}")

    # Preferences
    st.subheader("🧋 Describe your food preferences (Likes and Dislikes)")
    meal_pref = st.text_input("")

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
        preference_data = {"meal_pref": meal_pref}

        return user_data, preference_data

    return None, None


def display_results(results):
    st.header("📊 Your Meal Plan!")
    df = pd.DataFrame(results)
    st.dataframe(df)


def main():
    st.title("Meal Swipe Manager")
    st.write("Helping you plan your meal swipes efficiently!")

    user_data, preference_data = user_input()

    if user_data:
        quarter = user_data['quarter']
        swipes = user_data['swipes']
        selected_days = user_data['selected_days']
        excluded_weeks = user_data['excluded_weeks']

        diff_weeks = meal_distribution.get_weeks(quarter)

        if user_data['distribution'] == "Evenly throughout the quarter":
            results = meal_distribution.even_weekly_meals(
                swipes, selected_days, quarter, diff_weeks
            )
        else:
            results = meal_distribution.uneven_weekly_meals(
                swipes, selected_days, quarter, diff_weeks, excluded_weeks
            )

        display_results(results)
        
    # TODO: delete this later?
    if user_data and preference_data:
        st.success("Data successfully collected!")

        st.write("Swipe Data:", user_data)
        st.write("Preference Data:", preference_data)


if __name__ == "__main__":
    main()
