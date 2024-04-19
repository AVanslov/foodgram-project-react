def create_report_about_ingredient(ingredient_number, ingredient):
    return ' '.join(
        str(ingredient_number),
        ingredient.name,
        str(ingredient.ingredient_amount),
        ingredient.measurement_unit
    )
