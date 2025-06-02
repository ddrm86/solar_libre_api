FROM python:3.13-alpine
LABEL authors="david.delrio"

WORKDIR /code
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
COPY . /code/app
COPY render_config/initial_data.db /code/app/solar_libre.db
WORKDIR /code/app
EXPOSE 8000
CMD ["python", "main.py"]
