FROM python:3.10.4-slim as python

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1



RUN apt-get update && apt-get install -y --no-install-recommends \
    && apt-get clean 



RUN pip install --upgrade pip
RUN pip install "psycopg[binary, pool]"
COPY ./requirements .
RUN pip install --no-cache-dir -r local.txt

COPY ./scripts/start.sh /


RUN sed -i 's/\r$//g' /start.sh && chmod +x /start.sh &&


WORKDIR /app