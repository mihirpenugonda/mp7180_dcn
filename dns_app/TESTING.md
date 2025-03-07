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

## Kubernetes Deployment

### 1. Build and Tag Images

```bash
# Build images
docker-compose build

# Tag images for Kubernetes
docker tag auth_server-as:latest auth_server-as:latest
docker tag auth_server-fs:latest auth_server-fs:latest
docker tag auth_server-us:latest auth_server-us:latest
```

### 2. Deploy to Kubernetes

```bash
kubectl apply -f deploy_dns.yml
```

### 3. Verify Deployments

```bash
kubectl get deployments
kubectl get services
kubectl get pods
```

## Testing in Kubernetes Environment

1. Register Fibonacci Server:

```bash
curl -X PUT -H "Content-Type: application/json" \
  -d '{
    "hostname": "fibonacci.com",
    "ip": "fs-service",
    "as_ip": "as-service",
    "as_port": "53533"
  }' \
  http://<node-ip>:30002/register
```

2. Calculate Fibonacci Numbers (Direct to FS):

```bash
curl "http://<node-ip>:30002/fibonacci?number=10"
```

3. User Server Requests (Through DNS Resolution):

```bash
curl "http://<node-ip>:30003/fibonacci?hostname=fibonacci.com&fs_port=9090&number=10&as_ip=as-service&as_port=53533"
```

Note: Replace `<node-ip>` with your Kubernetes node IP address.

## Port Mappings in Kubernetes

- AS (Authoritative Server): NodePort 30001 (UDP)
- FS (Fibonacci Server): NodePort 30002
- US (User Server): NodePort 30003

## Common Issues and Debugging in Kubernetes

1. Check pod status:

```bash
kubectl get pods
kubectl describe pod <pod-name>
```

2. View pod logs:

```bash
kubectl logs <pod-name>
```

3. Check service status:

```bash
kubectl get services
kubectl describe service <service-name>
```

4. If pods are not starting:

- Check image pull policy
- Verify image names are correct
- Check pod events with `kubectl describe pod`

5. If services are not accessible:

- Verify node IP address
- Check if pods are running and ready
- Verify service nodePort configurations
