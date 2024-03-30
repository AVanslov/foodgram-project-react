"""Обработчик файла json. Формирует json файл с дополнительными полями."""

import json

with open('ingredients.json', 'r') as read_file:
    data = json.load(read_file)

new_json = []
for i, dictinary in enumerate(data, start=1):

    new_json.append(
        {
            "model": "foodgram_api.ingredient",
            "pk": i,
            "fields": dictinary,
        }
    )

with open("data.json", "w") as write_file:
    json.dump(new_json, write_file, ensure_ascii=False)
