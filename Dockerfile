FROM python:3.12-slim-bookworm

ENV PYTHONUNBUFFERED=1

ENV API_KEY=
ENV USER_ID=
ENV PLAYER_NAME=
ENV PLATFORM=
ENV DEBUG=false

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY server/ .

EXPOSE 5000

ENTRYPOINT [ "python", "main.py" ]
