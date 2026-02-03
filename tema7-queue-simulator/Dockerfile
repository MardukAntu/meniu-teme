FROM python:3.12-slim

WORKDIR /app
COPY . .

CMD ["python", "queue_simulator.py", "--clients", "100", "--arrival_rate", "0.3", "--service_rate", "0.5"]
