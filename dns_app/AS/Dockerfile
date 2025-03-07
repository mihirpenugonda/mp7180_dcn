FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
COPY authoritative_server.py .

EXPOSE 53533/udp

CMD ["python", "authoritative_server.py"] 