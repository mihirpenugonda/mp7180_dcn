FROM python:3.9-slim

# Install curl for health checks
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
COPY authoritative_server.py .

EXPOSE 53533/udp
EXPOSE 8053

CMD ["python", "authoritative_server.py"] 