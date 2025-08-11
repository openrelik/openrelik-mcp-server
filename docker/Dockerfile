FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl

RUN pip install uv

ADD . /app
WORKDIR /app
RUN uv sync --all-groups

ENV PYTHONPATH=/app

CMD ["uv", "run", "fastmcp", "run", "main.py", "--transport", "http", "--host", "0.0.0.0", "--port", "8081"]
