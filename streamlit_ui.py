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
        ['Fall 2025', 'Winter 2026', 'Spring 2026']
    )

    diff_weeks = meal_distribution.get_weeks(quarter)
    if diff_weeks == -1:
        st.error("This quarter hasn't started yet.")
        st.stop()
    
    if diff_weeks == 0:
        st.warning("This quarter has already ended.")
        st.stop()

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
            time.sleep(5)
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


def highlight_weeks(row):
    """
    Color rows by week label
    """
    week_label = row["Week Label"]
    color = f"hsl({(hash(week_label) % 360)}, 70%, 90%)"
    return ["background-color: " + color] * len(row)


def highlight_food(row):
    """
    Highlight only the Date column if favorite food exists.
    """
    styles = [""] * len(row)

    if pd.notna(row.get("Lunch")) or pd.notna(row.get("Dinner")):
        try:
            idx = row.index.get_loc("Date")  # find Date column position
            styles[idx] = "background-color: #d4f8d4"
        except KeyError:
            pass

    return styles

def display_results(results, lunch_dict=None, dinner_dict=None):
    '''
    Output of the Meal Plan
    '''
    st.header("📊 Your Meal Plan!")

    # List into Data Frame
    swipe_df = pd.DataFrame(results)

    if lunch_dict:
        lunch_df = pd.DataFrame(list(lunch_dict.items()), columns=["Date", "Lunch"])
        swipe_df = swipe_df.merge(lunch_df, on="Date", how="left")

    if dinner_dict:
        dinner_df = pd.DataFrame(list(dinner_dict.items()), columns=["Date", "Dinner"])
        swipe_df = swipe_df.merge(dinner_df, on="Date", how="left")

    if swipe_df.empty:
        st.warning("No meal plan data available.")
        return
    
    # Converting Date Column
    if "Date" in swipe_df.columns:
        swipe_df["Date"] = pd.to_datetime(swipe_df["Date"]).dt.strftime("%B %d, %Y")

    # Create label mapping
    week_map = {
        week: ("Finals Week" if week == 11 else f"Week {week}")
        for week in sorted(swipe_df["Week"].unique())
    }

    # Reverse mapping (label -> number)
    reverse_week_map = {v: k for k, v in week_map.items()}

    # Filtering!!
    st.subheader("🔎 Filter Your Plan")

    col1, col2, col3 = st.columns(3)

    with col1:
        week_filter = st.multiselect(
            "Filter by Week",
            options=list(week_map.values()),
            key="week_filter"
            )

    with col2:
        day_filter = st.multiselect(
            "Filter by Day",
            options=sorted(swipe_df["Day"].unique()),
            key="day_filter"
            )

    fav_only = st.checkbox(
        "Show only days with favorite food",
        key="fav_only"
        )
    
    # Applying Filters
    filtered_df = swipe_df.copy()

    if week_filter:
        selected_weeks = [reverse_week_map[label] for label in week_filter]
        filtered_df = filtered_df[filtered_df["Week"].isin(selected_weeks)]

    if day_filter:
        filtered_df = filtered_df[filtered_df["Day"].isin(day_filter)]

    if fav_only:
        filtered_df = filtered_df[
            filtered_df["Lunch"].notna() | filtered_df["Dinner"].notna()
        ]

    # Considering Finals Week
    filtered_df["Week Label"] = filtered_df["Week"].apply(
        lambda x: "Finals Week" if x == 11 else f"Week {x}"
    )

    columns = ["Date", "Week Label", "Day", "Meals"]

    if "Lunch" in filtered_df.columns:
        columns.append("Lunch")
    if "Dinner" in filtered_df.columns:
        columns.append("Dinner")

    filtered_df = filtered_df[columns]

    styled_df = (
        filtered_df
        .style
        .apply(highlight_weeks, axis=1)
        .apply(highlight_food, axis=1)
    )

    st.dataframe(
        styled_df,
        use_container_width=True,
        hide_index=True,
        column_config={"Week": None}
    )


def main():
    st.title("Meal Swipe Manager")
    st.write("Helping you plan your meal swipes efficiently!")

    user_data, preference_data = user_input()

    # If button was clicked, calculate and store in session_state
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

        # STORE results permanently
        st.session_state["results"] = results

    # If results exist, display with AI dictionaries (hardcoded test)
    if "results" in st.session_state:

        # Hardcoded AI lunch and dinner dictionaries
        lunch_dict = {'2026-03-05': 'Paneer Tikka Masala',
                       '2026-03-02': 'Chana Masala'
                       }

        dinner_dict = {'2026-03-10': 'Vegetable Curry'}

        display_results(
            st.session_state["results"],
            lunch_dict=lunch_dict,
            dinner_dict=dinner_dict
        )


if __name__ == "__main__":
    main()
