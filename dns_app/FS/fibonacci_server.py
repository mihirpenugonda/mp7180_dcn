from flask import Flask, request, jsonify
import socket
import json
import os
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[FS] %(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

app = Flask("fibonacci_server")
app.logger.handlers = logger.handlers
app.logger.setLevel(logger.level)

# Global variables to store configuration
config = {
    'hostname': os.getenv('FIBONACCI_HOSTNAME', 'fibonacci.com'),
    'ip': os.getenv('FIBONACCI_IP', '0.0.0.0'),
    'port': os.getenv('FIBONACCI_PORT', '9090')
}

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

@app.route('/fibonacci', methods=['GET'])
def fibonacci():
    try:
        number = request.args.get('number')
        if not number:
            logger.error("Missing number parameter")
            return jsonify({'error': 'Missing number parameter'}), 400
            
        number = int(number)
        logger.info(f"Calculating Fibonacci number for n={number}")
        result = calculate_fibonacci(number)
        logger.info(f"Fibonacci calculation result: {result}")
        return jsonify({'fibonacci': result}), 200
        
    except ValueError:
        logger.error(f"Invalid number format: {number}")
        return jsonify({'error': 'Invalid number format'}), 400
    except Exception as e:
        logger.error(f"Error calculating Fibonacci: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    logger.info(f"Starting Fibonacci Server on port {config['port']}")
    app.run(host='0.0.0.0', port=int(config['port'])) 