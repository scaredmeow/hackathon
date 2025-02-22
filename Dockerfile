FROM python:3.12-slim

WORKDIR /code

COPY ./requirements.lock /code/requirements.lock

RUN PYTHONDONTWRITEBYTECODE=1 pip install --no-cache-dir -r requirements.lock

COPY ./app /code/app
COPY . .

CMD ["fastapi", "run", "app/main.py", "--port", "80"]
