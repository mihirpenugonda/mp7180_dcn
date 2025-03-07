from flask import Flask, request, jsonify
import socket
import json

app = Flask(__name__)

# Global variables to store configuration
config = {
    'hostname': None,
    'ip': None,
    'as_ip': None,
    'as_port': None
}

def register_with_as():
    """Register the Fibonacci server with the Authoritative Server"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # Prepare DNS registration message
    message = (
        f"TYPE=A\n"
        f"NAME={config['hostname']}\n"
        f"VALUE={config['ip']}\n"
        f"TTL=10\n"
    )
    
    try:
        # Send registration message
        sock.sendto(message.encode(), (config['as_ip'], int(config['as_port'])))
        
        # Wait for response
        sock.settimeout(5)
        response, _ = sock.recvfrom(1024)
        return response.decode() == "OK"
    except Exception as e:
        print(f"Registration error: {e}")
        return False
    finally:
        sock.close()

def calculate_fibonacci(n):
    """Calculate the nth Fibonacci number"""
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b

@app.route('/register', methods=['PUT'])
def register():
    try:
        data = request.get_json()
        required_fields = ['hostname', 'ip', 'as_ip', 'as_port']
        
        # Validate request body
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Update configuration
        config.update(data)
        
        # Register with Authoritative Server
        if register_with_as():
            return '', 201
        else:
            return jsonify({'error': 'Failed to register with Authoritative Server'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/fibonacci', methods=['GET'])
def fibonacci():
    try:
        number = request.args.get('number')
        if not number:
            return jsonify({'error': 'Missing number parameter'}), 400
            
        number = int(number)
        result = calculate_fibonacci(number)
        return jsonify({'fibonacci': result}), 200
        
    except ValueError:
        return jsonify({'error': 'Invalid number format'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9090) 