from flask import Flask, request, jsonify
import socket
import requests
import os
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[US] %(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

app = Flask("user_server")
app.logger.handlers = logger.handlers
app.logger.setLevel(logger.level)

def register_with_as(hostname, ip, as_ip, as_port):
    """Register a hostname with the Authoritative Server"""
    logger.info(f"Attempting to register {hostname} → {ip} with AS at {as_ip}:{as_port}")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    message = (
        f"TYPE=A\n"
        f"NAME={hostname}\n"
        f"VALUE={ip}\n"
        f"TTL=10\n"
    )
    
    try:
        # Set a shorter timeout
        sock.settimeout(5)
        sock.sendto(message.encode(), (as_ip, int(as_port)))
        response, _ = sock.recvfrom(1024)
        success = response.decode() == "OK"
        
        if success:
            logger.info(f"Successfully registered {hostname}")
        else:
            logger.error(f"Failed to register {hostname}")
        return success
    except socket.timeout:
        logger.error(f"Registration timed out while trying to connect to {as_ip}:{as_port}")
        return False
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        return False
    finally:
        sock.close()

def query_dns(hostname, as_ip, as_port):
    """Query the Authoritative Server for hostname resolution"""
    logger.info(f"Querying DNS for {hostname} at {as_ip}:{as_port}")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    message = (
        f"TYPE=A\n"
        f"NAME={hostname}\n"
    )
    
    try:
        sock.sendto(message.encode(), (as_ip, int(as_port)))
        sock.settimeout(5)
        response, _ = sock.recvfrom(1024)
        response = response.decode()
        
        if response != "NOT_FOUND":
            lines = response.strip().split('\n')
            for line in lines:
                if line.startswith('VALUE='):
                    ip = line.split('=')[1]
                    logger.info(f"DNS resolution successful: {hostname} → {ip}")
                    return ip
        logger.warning(f"DNS resolution failed for {hostname}")
        return None
    except Exception as e:
        logger.error(f"DNS query error: {str(e)}")
        return None
    finally:
        sock.close()

@app.route('/register', methods=['PUT'])
def register():
    """Register a Fibonacci server with the AS"""
    try:
        data = request.get_json()
        required_fields = ['hostname', 'ip', 'as_ip', 'as_port']
        
        if not all(field in data for field in required_fields):
            logger.error("Missing required fields in registration request")
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Use the container name 'as' if as_ip is localhost or 127.0.0.1
        as_ip = data['as_ip']
        if as_ip in ['localhost', '127.0.0.1']:
            as_ip = os.getenv('AS_IP', 'as')
            logger.info(f"Converting localhost to container name: {as_ip}")
        
        success = register_with_as(
            data['hostname'],
            data['ip'],
            as_ip,
            data['as_port']
        )
        
        if success:
            return '', 201
        return jsonify({'error': 'Registration failed'}), 500
            
    except Exception as e:
        logger.error(f"Registration request error: {str(e)}")
        return jsonify({'error': str(e)}), 400

@app.route('/fibonacci')
def fibonacci():
    params = ['hostname', 'fs_port', 'number', 'as_ip', 'as_port']
    values = {param: request.args.get(param) for param in params}
    
    if not all(values.values()):
        logger.error("Missing required parameters in fibonacci request")
        return jsonify({'error': 'Missing required parameters'}), 400
        
    try:
        fs_ip = query_dns(values['hostname'], values['as_ip'], values['as_port'])
        if not fs_ip:
            return jsonify({'error': 'Could not resolve hostname'}), 404
            
        fs_url = f"http://{fs_ip}:{values['fs_port']}/fibonacci"
        logger.info(f"Forwarding request to Fibonacci server at {fs_url}")
        
        response = requests.get(fs_url, params={'number': values['number']})
        logger.info(f"Received response from Fibonacci server: {response.status_code}")
        
        return response.json(), response.status_code
        
    except requests.RequestException as e:
        logger.error(f"Failed to contact Fibonacci server: {str(e)}")
        return jsonify({'error': f'Failed to contact Fibonacci server: {str(e)}'}), 503
    except Exception as e:
        logger.error(f"Unexpected error in fibonacci request: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    logger.info("Starting User Server on port 8080")
    app.run(host='0.0.0.0', port=8080) 