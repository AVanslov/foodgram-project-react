def create_report_about_ingredient(ingredient_number, ingredient):
    return str(ingredient_number) + ' '.join(
        str(key) + ': ' + str(value)
        for key, value in ingredient.items()
        if value
    )
