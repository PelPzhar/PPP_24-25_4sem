import socket
import json
import csv
from io import StringIO
from logger import Logger

class Client:
    def __init__(self, host="127.0.0.1", port=12345):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.logger = Logger("client.log")

    def connect(self):
        self.socket.connect((self.host, self.port))
        # Аутентификация
        self.socket.send("user:password".encode())
        response = self.socket.recv(1024).decode()
        print(response)
        if "failed" in response.lower():
            self.socket.close()
            return False
        self.logger.log("Connected to server")
        return True

    def run(self):
        if not self.connect():
            return

        while True:
            print("\n1. Send SELECT query")
            print("2. Get tables structure")
            print("3. Exit")
            choice = input("Choose an option: ")

            if choice == "1":
                query = input("Enter SELECT query (e.g., SELECT * FROM table WHERE column = value): ")
                self.send_query(query)
            elif choice == "2":
                self.get_tables_structure()
            elif choice == "3":
                break
            else:
                print("Invalid choice")

        self.socket.close()
        self.logger.log("Disconnected from server")

    def send_query(self, query):
        print("Sending query...")
        self.socket.send(query.encode('utf-8'))
        print("Query sent, waiting for response...")
        response = ""
        try:
            while True:
                part = self.socket.recv(4096).decode('utf-8', errors='replace')
                print(f"Received part: {part}")
                if not part:
                    break
                response += part
                if len(part) < 4096:
                    break
        except Exception as e:
            print(f"Error receiving response: {str(e)}")
            self.logger.log(f"Error receiving response: {str(e)}")
            return

        self.logger.log(f"Sent query: {query}")
        print("Server response:")
        print(f"Raw response: {response}")
        if not response:
            print("No response from server")
            self.logger.log("No response from server")
            return
        if response.startswith("Error") or "not found" in response.lower() or response == "No data found":
            print(f"Error: {response}")
            self.logger.log(f"Error response: {response}")
            return

        # Если это CSV, отображаем как таблицу
        try:
            # Убираем лишние пустые строки
            cleaned_response = '\n'.join(line for line in response.splitlines() if line.strip())
            csv_file = StringIO(cleaned_response)
            reader = csv.reader(csv_file)
            for row in reader:
                print(row)
            self.logger.log("Received query result")
        except Exception as e:
            print(f"Failed to parse response as CSV: {response}")
            self.logger.log(f"Failed to parse response: {str(e)}")

    def get_tables_structure(self):
        self.socket.send("GET_TABLES".encode())
        response = self.socket.recv(4096).decode()
        structure = json.loads(response)
        print("\nTables structure:")
        for table, columns in structure.items():
            print(f"Table: {table}")
            print(f"Columns: {', '.join(columns)}")
        self.logger.log("Received tables structure")

def run_client():
    client = Client()
    client.run()