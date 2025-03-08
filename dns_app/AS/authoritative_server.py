import socket
import json
import os
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[AS] %(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Constants
UDP_PORT = 53533
BUFFER_SIZE = 1024
DNS_DB_FILE = "/tmp/dns_records.json"

class AuthoritativeServer:
    def __init__(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind(('0.0.0.0', UDP_PORT))
            self.dns_records = self.load_dns_records()
            logger.info(f"Authoritative Server is running on UDP port {UDP_PORT}")
            logger.info("Waiting for DNS queries and registrations...")
        except Exception as e:
            logger.error(f"Failed to initialize server: {e}", exc_info=True)
            raise

    def load_dns_records(self):
        try:
            if os.path.exists(DNS_DB_FILE):
                with open(DNS_DB_FILE, 'r') as f:
                    records = json.load(f)
                    logger.info(f"Loaded {len(records)} DNS records from {DNS_DB_FILE}")
                    return records
            logger.info(f"No existing DNS records found, starting fresh")
            return {}
        except Exception as e:
            logger.error(f"Error loading DNS records: {e}")
            return {}

    def save_dns_records(self):
        try:
            os.makedirs(os.path.dirname(DNS_DB_FILE), exist_ok=True)
            with open(DNS_DB_FILE, 'w') as f:
                json.dump(self.dns_records, f)
                logger.info(f"Saved {len(self.dns_records)} DNS records to {DNS_DB_FILE}")
        except Exception as e:
            logger.error(f"Error saving DNS records: {e}")

    def handle_registration(self, data, addr):
        try:
            lines = data.strip().split('\n')
            record = {}
            
            for line in lines:
                if '=' in line:
                    key, value = line.split('=', 1)
                    record[key] = value

            if 'TYPE' in record and 'NAME' in record and 'VALUE' in record and 'TTL' in record:
                key = f"{record['NAME']}:{record['TYPE']}"
                self.dns_records[key] = {
                    'value': record['VALUE'],
                    'ttl': record['TTL']
                }
                self.save_dns_records()
                logger.info(f"Registered DNS record for {record['NAME']} → {record['VALUE']} from {addr}")
                return "OK"
            logger.error(f"Invalid registration data from {addr}: {data}")
            return "FAIL"
        except Exception as e:
            logger.error(f"Error handling registration from {addr}: {e}")
            return "FAIL"

    def handle_query(self, data, addr):
        try:
            lines = data.strip().split('\n')
            query = {}
            
            for line in lines:
                if '=' in line:
                    key, value = line.split('=', 1)
                    query[key] = value

            if 'TYPE' in query and 'NAME' in query:
                key = f"{query['NAME']}:{query['TYPE']}"
                if key in self.dns_records:
                    record = self.dns_records[key]
                    response = (
                        f"TYPE={query['TYPE']}\n"
                        f"NAME={query['NAME']}\n"
                        f"VALUE={record['value']}\n"
                        f"TTL={record['ttl']}\n"
                    )
                    logger.info(f"DNS query from {addr}: {query['NAME']} → {record['value']}")
                    return response
            logger.warning(f"DNS query from {addr}: {query.get('NAME', 'unknown')} → Not found")
            return "NOT_FOUND"
        except Exception as e:
            logger.error(f"Error handling query from {addr}: {e}")
            return "NOT_FOUND"

    def run(self):
        logger.info("Starting main UDP server loop")
        while True:
            try:
                data, addr = self.socket.recvfrom(BUFFER_SIZE)
                data = data.decode('utf-8')
                logger.info(f"Received request from {addr}")
                
                # Check if it's a registration (has VALUE and TTL) or query
                if 'VALUE=' in data and 'TTL=' in data:
                    response = self.handle_registration(data, addr)
                else:
                    response = self.handle_query(data, addr)

                self.socket.sendto(response.encode('utf-8'), addr)
            except Exception as e:
                logger.error(f"Error in main loop: {e}")

if __name__ == "__main__":
    try:
        server = AuthoritativeServer()
        server.run()
    except Exception as e:
        logger.error(f"Server failed to start: {e}", exc_info=True)
        sys.exit(1) 