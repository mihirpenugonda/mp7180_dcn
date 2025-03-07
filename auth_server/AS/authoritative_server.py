import socket
import json
import os

# Constants
UDP_PORT = 53533
BUFFER_SIZE = 1024
DNS_DB_FILE = "dns_records.json"

class AuthoritativeServer:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(('0.0.0.0', UDP_PORT))
        self.dns_records = self.load_dns_records()

    def load_dns_records(self):
        if os.path.exists(DNS_DB_FILE):
            with open(DNS_DB_FILE, 'r') as f:
                return json.load(f)
        return {}

    def save_dns_records(self):
        with open(DNS_DB_FILE, 'w') as f:
            json.dump(self.dns_records, f)

    def handle_registration(self, data):
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
            return True
        return False

    def handle_query(self, data):
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
                return response
        return None

    def run(self):
        print(f"Authoritative Server listening on UDP port {UDP_PORT}")
        while True:
            try:
                data, addr = self.socket.recvfrom(BUFFER_SIZE)
                data = data.decode('utf-8')
                
                # Check if it's a registration (has VALUE and TTL) or query
                if 'VALUE=' in data and 'TTL=' in data:
                    success = self.handle_registration(data)
                    response = "OK" if success else "FAIL"
                else:
                    response = self.handle_query(data)
                    if not response:
                        response = "NOT_FOUND"

                self.socket.sendto(response.encode('utf-8'), addr)
            except Exception as e:
                print(f"Error: {e}")

if __name__ == "__main__":
    server = AuthoritativeServer()
    server.run() 