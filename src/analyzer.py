import pandas as pd

def load_ingredient_database():
    data = pd.read_csv("data/ingredient_database.csv")
    return data

def analyze_ingredients(user_ingredients, database):
    analysis_results = []
    for ingredient in user_ingredients:
        match = database[database['Ingredient'].str.lower() == ingredient.lower()]
        if not match.empty:
            row = match.iloc[0].to_dict()
        else:
            row = {
                "Ingredient": ingredient,
                "Function": "Unknown",
                "Risk Level": "Unknown",
                "Description": "Not found in database."
            }
        analysis_results.append(row)
    return analysis_results
