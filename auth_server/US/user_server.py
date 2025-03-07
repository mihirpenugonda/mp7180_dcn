from flask import Flask, request, jsonify
import socket
import requests

app = Flask(__name__)

def query_dns(hostname, as_ip, as_port):
    """Query the Authoritative Server for hostname resolution"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # Prepare DNS query message
    message = (
        f"TYPE=A\n"
        f"NAME={hostname}\n"
    )
    
    try:
        # Send query
        sock.sendto(message.encode(), (as_ip, int(as_port)))
        
        # Wait for response
        sock.settimeout(5)
        response, _ = sock.recvfrom(1024)
        response = response.decode()
        
        # Parse response
        if response != "NOT_FOUND":
            lines = response.strip().split('\n')
            for line in lines:
                if line.startswith('VALUE='):
                    return line.split('=')[1]
        return None
        
    except Exception as e:
        print(f"DNS query error: {e}")
        return None
    finally:
        sock.close()

@app.route('/fibonacci')
def fibonacci():
    # Get and validate required parameters
    params = ['hostname', 'fs_port', 'number', 'as_ip', 'as_port']
    values = {param: request.args.get(param) for param in params}
    
    # Check if any parameter is missing
    if not all(values.values()):
        return jsonify({'error': 'Missing required parameters'}), 400
        
    try:
        # Query DNS for hostname resolution
        fs_ip = query_dns(values['hostname'], values['as_ip'], values['as_port'])
        if not fs_ip:
            return jsonify({'error': 'Could not resolve hostname'}), 404
            
        # Forward request to Fibonacci server
        fs_url = f"http://{fs_ip}:{values['fs_port']}/fibonacci"
        response = requests.get(fs_url, params={'number': values['number']})
        
        # Return the response from Fibonacci server
        return response.json(), response.status_code
        
    except requests.RequestException as e:
        return jsonify({'error': f'Failed to contact Fibonacci server: {str(e)}'}), 503
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080) 