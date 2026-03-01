from google import genai
import os
import json
import math
import ast

brandywine_menu = "/Users/harinis/meal-plan-manager/brandywine_menu.json"

meal_distribution = [
    {'Date': '2026-03-01', 'Week': 1, 'Day': 'Tuesday', 'Meals': 2},
    {'Date': '2026-03-02', 'Week': 1, 'Day': 'Thursday', 'Meals': 1},
]


def get_total_meals_per_days(meal_distribution):
    total_meals_per_days = []
    current_week = meal_distribution[0]["Week"]
    week_total = 0
    week_dates = []

    for entry in meal_distribution:
        if entry["Week"] != current_week:
            total_meals_per_days.append({week_total: week_dates})

            current_week = entry["Week"]
            week_total = 0
            week_dates = []

        week_total += entry["Meals"]
        week_dates.append(entry["Date"])

    total_meals_per_days.append({week_total: week_dates})

    return total_meals_per_days


def get_relevant_date(weekly, favorite_lunches, favorite_dinners):
    for week in weekly:
        for total_meals, dates in week.items():
            if total_meals // len(dates) < 2:
                if dates[0] in favorite_dinners:
                    return week


lunch = {'2025-09-23': '"Vegetable Curry"', '2025-09-30': '""', '2026-03-03': '"Paneer Butter Masala"', '2026-03-04': '""', '2026-03-05': '"Spicy Tofu Bowl"', '2026-03-06': '""', '2026-03-07': '"Paneer Tikka"'}


# this part should only run if relevant dates is not empty
def distribute_scarce_meals(relevant_date, best_lunches, best_dinners):
    lunches_to_choose_from = {}
    dinners_to_choose_from = {}
    total_meals = list(relevant_date.items())[0][0]
    dates = list(relevant_date.items())[0][1]
    total_lunches = math.ceil(total_meals / len(dates))
    total_dinners = math.floor(total_meals / len(dates))


    for date in dates:
        if date in best_lunches:
            lunches_to_choose_from[date] = best_lunches[date]

        if date in best_dinners:
            dinners_to_choose_from[date] = best_dinners[date]

    optimal_lunches, optimal_dinners = get_meal_distribution(lunches_to_choose_from, dinners_to_choose_from, total_lunches, total_dinners)


    optimal_lunch_list = ast.literal_eval(optimal_lunches)
    optimal_dinner_list = ast.literal_eval(optimal_dinners)

    
    final_lunch_dict = {}
    inverted_lunch = {v: k for k, v in lunches_to_choose_from.items()}
    for lunch in optimal_lunch_list:
        date = inverted_lunch[lunch]
        final_lunch_dict[date] = lunch

    final_dinner_dict = {}
    inverted_dinner = {v: k for k, v in dinners_to_choose_from.items()}
    for dinner in optimal_dinner_list:
        date = inverted_dinner[dinner]
        final_dinner_dict[date] = dinner
    
    return (final_lunch_dict, final_dinner_dict)




def get_meal_distribution(available_lunch_meals, available_dinner_meals, num_lunch, num_dinner):
    client = genai.Client(api_key = os.getenv("GEMINI_API_KEY"))
    lunch_response = client.models.generate_content(
    model = 'gemini-2.5-flash', 
    contents = f"""Please take a look at the available meals and the user's food preferences and please output the meal the user will best like.

    Here are the available meals: Lunch: {available_lunch_meals.values()}

    Here are the user preferences: {meal_likes}

    Please recommend exactly {num_lunch} lunch meals that the user will like and make sure their dietary restrictions are met and please return precicely only one list containing exactly {num_lunch} meals the user will like, with exact meal spelling, and make the meals each a string and absolutely nothing else (precisely no reason or extra commentary at all).""",
    config = {
    "response_mime_type": "application/json",
    "response_schema": {
        "type": "array",
        "items": {
            "type": "string"
            }
        }
    }  
    )

    dinner_response = client.models.generate_content(
    model = 'gemini-2.5-flash', 
    contents = f"""Please take a look at the available meals and the user's food preferences and please output the meal the user will best like.

    Here are the available meals: Dinner: {available_dinner_meals.values()}

    Here are the user preferences: {meal_likes}

    Please recommend exactly {num_dinner} dinner meals that the user will like and make sure their dietary restrictions are met and please return precicely only one list containing exactly {num_dinner} meals the user will like, with exact meal spelling, and make the meals each a string and absolutely nothing else (precisely no reason or extra commentary at all).""",
    config = {
    "response_mime_type": "application/json",
    "response_schema": {
        "type": "array",
        "items": {
            "type": "string"
            }
        }
    }  
    )

    return (lunch_response.text, dinner_response.text)


meal_likes = "vegetarian, no meat, no fish, like Indian food, like spicy food, no plant-based beef, no sweet tofu"

def get_meals_dict(menu_path) -> dict:
    """Takes json file path containing available meals as input and returns a dict containing all meals"""
    with open(menu_path, 'r') as meal_file:
        meal_dict = json.load(meal_file)
    return meal_dict

def get_available_meals(meal_dict):
    """Takes a python dict and yields tuple containing all available meals for lunch and dinner for current day"""
    for day in meal_dict:
        yield (day, meal_dict[day]['Lunch'], meal_dict[day]["Dinner"])



def get_best_lunch_and_dinner(available_lunch_meals, available_dinner_meals, meal_likes):
    client = genai.Client(api_key = os.getenv("GEMINI_API_KEY"))
    
    lunch_response = client.models.generate_content(
    model = 'gemini-2.5-flash', 
    contents = f"""Please take a look at the available meals and the user's food preferences and please output the meal the user will best like.

    Here are the available meals: Lunch: {available_lunch_meals}

    Here are the user preferences: {meal_likes}

    Please recommend exactly one lunch meal that the user will like, make sure their dietary restrictions are met and please return precicely only a string containing the meal the user will like, with exact meal spelling, and absolutely nothing else (precisely no reason or extra commentary at all).""",
    config = {
        "response_mime_type": "application/json",
        "response_schema" : {
            "type": "string"
            }
        }  
    )

    dinner_response = client.models.generate_content(
    model = 'gemini-2.5-flash', 
    contents = f"""Please take a look at the available meals and the user's food preferences and please output the meal the user will best like.

    Here are the available meals: Dinner: {available_dinner_meals}

    Here are the user preferences: {meal_likes}

    Please recommend exactly one one dinner meal user will like make sure their dietary restrictions are met and please return precicely only a string containing the meal the user will like, with exact meal spelling, and absolutely nothing else (precisely no reason or extra commentary at all)""",
    config = {
        "response_mime_type": "application/json",
        "response_schema" : {
            "type": "string"
            }
        }  
    )

    return (lunch_response.text.strip('"'), dinner_response.text.strip('"'))


def get_best_lunch_and_dinner_for_week(meal_likes):
    meals_dict = get_meals_dict(brandywine_menu)
    meal_generator = get_available_meals(meals_dict)
    favorite_lunches = {}
    favorite_dinners = {}
    try:
        while True:
            next_day, next_lunch_menu, next_dinner_menu = next(meal_generator)
            best_lunch_meal, best_dinner_meal = get_best_lunch_and_dinner(next_lunch_menu, next_dinner_menu, meal_likes)
            favorite_lunches[next_day] = best_lunch_meal
            favorite_dinners[next_day] = best_dinner_meal
    except StopIteration:
        pass
    return favorite_lunches, favorite_dinners


def main():
    fav_lunches, fav_dinners = get_best_lunch_and_dinner_for_week(meal_likes)
    weekly = get_total_meals_per_days(meal_distribution)
    relevant_week = get_relevant_date(weekly, fav_lunches, fav_dinners)
    if relevant_week != None:
        best_lunch, best_dinner = distribute_scarce_meals(relevant_week, fav_lunches, fav_dinners)
        return best_lunch, best_dinner
    else:
        return fav_lunches, fav_dinners

print('Powered by Google Gemini API')


print(main())

