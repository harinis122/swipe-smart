# planning out the dates

from datetime import date
import math
from collections import defaultdict
from datetime import timedelta

today = date.today()
# selected_days from chloe

end_fall = date(2025, 12, 12)
end_winter = date(2026, 3, 20)
end_spring = date(2026, 6, 12)

def get_weeks(quarter):
    if quarter == 'Fall 2025':
        start = date(2025, 9, 22)
        end = end_fall
    elif quarter == 'Winter 2026':
        start = date(2026, 1, 2)
        end = end_winter
    elif quarter == "Spring 2026":
        start = date(2026, 3, 25)
        end = end_spring

    today = date.today()

    if today < start:
        return -1
    
    diff_days = (end - today).days
    diff_weeks = math.ceil(diff_days / 7)

    # Actual range
    diff_weeks = min(11, max(0, diff_weeks))
    return diff_weeks

def get_date(week, day, quarter):
    if quarter == 'Fall 2025':
        start = date(2025, 9, 25)
    elif quarter == 'Winter 2026':
        start = date(2026, 1, 5)
    elif quarter == 'Spring 2026':
        start = date(2026, 3, 30)

    start_week = start + timedelta(weeks = week - 1)

    ind = {
        'Monday': 0,
        'Tuesday': 1,
        'Wednesday': 2,
        'Thursday': 3,
        'Friday': 4,
        'Saturday': 5,
        'Sunday': 6
    }

    start_day = start_week.weekday()
    final_day = ind[day]
    diff_day = final_day - start_day

    actual = start_week + timedelta(days = diff_day)

    return actual.strftime("%Y-%m-%d")

def even_weekly_meals(swipes, selected_days, quarter, diff_weeks):
    if diff_weeks <= 0 or len(selected_days) == 0:
        return []
    
    total_slots = diff_weeks * len(selected_days)

    base = swipes // total_slots
    remainder = swipes % total_slots

    result = []
    slot_index = 0

    total_weeks = 11
    start_week = total_weeks - diff_weeks + 1

    for week in range(start_week, total_weeks + 1):
        for day in selected_days:
            meals = base
            if slot_index < remainder:
                meals += 1

            result.append({
            "Date": get_date(week, day, quarter),
            "Week": week,
            "Day": day, 
            "Meals": meals
            })
            
            slot_index += 1

    return result

def uneven_weekly_meals(swipes, selected_days, quarter, diff_weeks, excluded_weeks):
    #based on unchekd boxes, append excluded weeks to this list
    if diff_weeks <= 0 or len(selected_days) == 0:
        return []
    
    valid_weeks = []
    total_weeks = 11
    start_week = total_weeks - diff_weeks + 1

    for week in range(start_week, total_weeks + 1):
        if f"Week {week}" not in excluded_weeks:
            valid_weeks.append(week)

    available = []
    for week in valid_weeks:
        for day in selected_days:
            available.append((week, day))

    if len(available) == 0:
        return []

    min_meals = swipes // len(available)
    extra_meals = swipes % len(available)

    result = []

    for i, (week, day) in enumerate(available):
        meals_per_slot = min_meals
        if i < extra_meals:
            meals_per_slot += 1

        result.append({
            "Date": get_date(week, day, quarter),
            "Week": week,
            "Day": day, 
            "Meals": meals_per_slot
        })

    return result
