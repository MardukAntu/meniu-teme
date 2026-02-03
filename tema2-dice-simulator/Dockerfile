FROM python:3.12-slim

WORKDIR /app
COPY . .

CMD ["python", "dice-simulation.py", "--faces", "6", "--rolls", "1000", "--chart", "histogram"]
