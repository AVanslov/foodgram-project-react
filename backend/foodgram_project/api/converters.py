def create_report_about_ingredient(ingredient_number, ingredient):
    return (
        '<tr>'
        + '<th>'
        + str(ingredient_number) + '</th>'
        + ' '.join(
            '<th>' + str(value) + '</th>'
            for key, value in ingredient.items()
            if value and key != 'recipe__ingredients__measurement_unit'
        ) + '<th>'
        + str(ingredient['recipe__ingredients__measurement_unit']) + '</th>'
        + '</tr>'
    )


def create_full_report_about_ingredient(ingredients_data):
    header = (
        '''
            <style>
                table {
                    width: 100%; /* Ширина таблицы */
                    border-collapse: collapse; /* Убираем двойные рамки */
                }
                .table-title{
                    background-color: #CEE741;
                    color: white;
                }
                th {
                    border: 0px solid #ddd; /* Параметры рамки */
                    padding: 4px; /* Поля в ячейках */
                    font-family: 'Robert Sans', sans-serif;
                    font-size: 16px;
                }
                tr:hover {
                    background: #CEE741; /* Цвет фона */
                }
            </style>
            <table>
                <tr class="table-title">
                    <th><b>№</b></th>
                    <th><b>Продукт</b></th>
                    <th><b>Количество</b></th>
                    <th><b>Мера</b></th>
                </tr>
        '''
    )
    products_list = [
        create_report_about_ingredient(
            ingredient_number, ingredient
        ) for ingredient_number, ingredient
        in enumerate(ingredients_data, start=1)
    ]
    end_tag = '</table>'
    products_list.insert(0, header)
    products_list.append(end_tag)
    return products_list
