# Distributed DNS and Fibonacci System

This system consists of three components that work together to provide Fibonacci numbers through a DNS-based service discovery mechanism.

## Components

1. **AS (Authoritative Server)** - UDP server on port 53533

   - Handles DNS registration
   - Responds to DNS queries
   - Stores DNS records persistently

2. **FS (Fibonacci Server)** - HTTP server on port 9090

   - Registers itself with AS
   - Calculates Fibonacci numbers
   - Endpoints:
     - PUT /register - Register with AS
     - GET /fibonacci?number=X - Calculate Fibonacci number

3. **US (User Server)** - HTTP server on port 8080
   - Resolves hostnames through AS
   - Forwards requests to FS
   - Endpoint:
     - GET /fibonacci with parameters:
       - hostname
       - fs_port
       - number
       - as_ip
       - as_port

## Running with Docker

1. Build and start all services:

```bash
docker-compose up --build
```

2. Register Fibonacci Server:

```bash
curl -X PUT -H "Content-Type: application/json" -d '{
  "hostname": "fibonacci.com",
  "ip": "fs",
  "as_ip": "as",
  "as_port": "53533"
}' http://localhost:9090/register
```

3. Request Fibonacci number through User Server:

```bash
curl "http://localhost:8080/fibonacci?hostname=fibonacci.com&fs_port=9090&number=10&as_ip=as&as_port=53533"
```

## Project Structure

```
.
├── docker-compose.yml
├── AS/
│   ├── Dockerfile
│   ├── authoritative_server.py
│   └── requirements.txt
├── FS/
│   ├── Dockerfile
│   ├── fibonacci_server.py
│   └── requirements.txt
└── US/
    ├── Dockerfile
    ├── user_server.py
    └── requirements.txt
```

## Error Handling

- All servers implement proper error handling for invalid inputs
- Missing parameters return 400 Bad Request
- DNS resolution failures return 404 Not Found
- Network errors return appropriate 5xx status codes

## Development

To run services individually for development:

1. Authoritative Server (AS):

```bash
cd AS
python authoritative_server.py
```

2. Fibonacci Server (FS):

```bash
cd FS
pip install -r requirements.txt
python fibonacci_server.py
```

3. User Server (US):

```bash
cd US
pip install -r requirements.txt
python user_server.py
```
