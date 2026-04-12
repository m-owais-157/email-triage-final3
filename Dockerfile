FROM python:3.10-slim

WORKDIR /app

COPY . /app

RUN pip install -e .

CMD ["python", "server/app.py"]
