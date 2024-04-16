def create_report_about_ingredient(ingredient_number, ingredient):
    return ' '.join(
        [
            ingredient_number,
            ingredient.name,
            ingredient.ingredient_amount,
            ingredient.measurement_unit
        ]
    )