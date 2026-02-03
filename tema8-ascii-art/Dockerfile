FROM python:3.12-slim

WORKDIR /app
COPY . .

RUN pip install --no-cache-dir pillow

CMD ["python", "ascii_art.py", "--text", "HELLO", "--preview"]
