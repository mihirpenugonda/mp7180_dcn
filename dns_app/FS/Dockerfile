FROM python:3.9-slim

# Install curl for health checks
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY fibonacci_server.py .

EXPOSE 9090

CMD ["python", "fibonacci_server.py"] 