FROM python:3.9

WORKDIR /app

RUN pip install gunicorn==20.1.0

COPY requirements.txt .

COPY configured_ingredients.json .

COPY tags.json .

RUN pip install -r requirements.txt --no-cache-dir

COPY . .

# RUN python3 manage.py collectstatic

CMD ["gunicorn", "--bind", "0.0.0.0:7000", "foodgram_project.wsgi"]
