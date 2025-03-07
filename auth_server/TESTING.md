# Testing Guide

This document provides curl commands to test all endpoints of the distributed system. Make sure all services are running using `docker-compose up --build` before testing.

## 1. Register Fibonacci Server with AS

### Local Development

```bash
curl -X PUT -H "Content-Type: application/json" \
  -d '{
    "hostname": "fibonacci.com",
    "ip": "127.0.0.1",
    "as_ip": "127.0.0.1",
    "as_port": "53533"
  }' \
  http://localhost:9090/register

# Expected Response:
# Status: 201 Created
# (empty response body)
```

### Docker Environment

```bash
curl -X PUT -H "Content-Type: application/json" \
  -d '{
    "hostname": "fibonacci.com",
    "ip": "fs",
    "as_ip": "as",
    "as_port": "53533"
  }' \
  http://localhost:9090/register

# Expected Response:
# Status: 201 Created
# (empty response body)
```

## 2. Calculate Fibonacci Numbers (Direct to FS)

### Valid Request

```bash
curl "http://localhost:9090/fibonacci?number=10"

# Expected Response:
# Status: 200 OK
# {
#   "fibonacci": 55
# }
```

### Invalid Input

```bash
curl "http://localhost:9090/fibonacci?number=abc"

# Expected Response:
# Status: 400 Bad Request
# {
#   "error": "Invalid number format"
# }
```

### Missing Parameter

```bash
curl "http://localhost:9090/fibonacci"

# Expected Response:
# Status: 400 Bad Request
# {
#   "error": "Missing number parameter"
# }
```

## 3. User Server Requests (Through DNS Resolution)

### Local Development

```bash
curl "http://localhost:8081/fibonacci?hostname=fibonacci.com&fs_port=9090&number=10&as_ip=127.0.0.1&as_port=53533"

# Expected Response:
# Status: 200 OK
# {
#   "fibonacci": 55
# }
```

### Docker Environment

```bash
curl "http://localhost:8081/fibonacci?hostname=fibonacci.com&fs_port=9090&number=10&as_ip=as&as_port=53533"

# Expected Response:
# Status: 200 OK
# {
#   "fibonacci": 55
# }
```

### Missing Parameters

```bash
curl "http://localhost:8081/fibonacci?hostname=fibonacci.com&number=10"

# Expected Response:
# Status: 400 Bad Request
# {
#   "error": "Missing required parameters"
# }
```

### Unknown Hostname

```bash
curl "http://localhost:8081/fibonacci?hostname=unknown.com&fs_port=9090&number=10&as_ip=as&as_port=53533"

# Expected Response:
# Status: 404 Not Found
# {
#   "error": "Could not resolve hostname"
# }
```

### Invalid Number

```bash
curl "http://localhost:8081/fibonacci?hostname=fibonacci.com&fs_port=9090&number=abc&as_ip=as&as_port=53533"

# Expected Response:
# Status: 400 Bad Request
# {
#   "error": "Invalid number format"
# }
```

## Testing Sequence

For a complete test of the system, follow these steps in order:

1. Start all services:

```bash
docker-compose up --build
```

2. Register the Fibonacci Server:

```bash
curl -X PUT -H "Content-Type: application/json" \
  -d '{
    "hostname": "fibonacci.com",
    "ip": "fs",
    "as_ip": "as",
    "as_port": "53533"
  }' \
  http://localhost:9090/register
```

3. Test direct Fibonacci calculation:

```bash
curl "http://localhost:9090/fibonacci?number=10"
```

4. Test through User Server with DNS resolution:

```bash
curl "http://localhost:8081/fibonacci?hostname=fibonacci.com&fs_port=9090&number=10&as_ip=as&as_port=53533"
```

## Common Issues and Debugging

1. If registration fails:

   - Check if AS is running and accessible
   - Verify the AS IP and port are correct
   - Check network connectivity between containers

2. If Fibonacci calculation fails:

   - Verify FS is running
   - Check if the number parameter is valid
   - Verify the port number is correct

3. If DNS resolution fails:
   - Verify the hostname was properly registered
   - Check if AS can be reached
   - Verify the DNS record hasn't expired (TTL)

Note: The User Server (US) is now running on port 8081 instead of 8080 to avoid port conflicts.
