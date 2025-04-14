import socket
import threading
import csv
import json
import os
from parser import parse_sql
from cache import Cache
from logger import Logger
from auth import authenticate
from tempfile import NamedTemporaryFile

class Server:
    def __init__(self, host="127.0.0.1", port=12345):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.host, self.port))
        self.socket.listen(5)
        self.cache = Cache()
        self.logger = Logger("server.log")
        self.tables_dir = "tables"

    def run(self):
        self.logger.log("Server started")
        print(f"Server listening on {self.host}:{self.port}")
        while True:
            client_socket, addr = self.socket.accept()
            threading.Thread(target=self.handle_client, args=(client_socket, addr)).start()

    def handle_client(self, client_socket, addr):
        self.logger.log(f"New connection from {addr}")
        try:
            # Аутентификация
            auth_data = client_socket.recv(1024).decode()
            if not authenticate(auth_data):
                client_socket.send("Authentication failed".encode())
                client_socket.close()
                return

            client_socket.send("Authentication successful".encode())
            while True:
                data = client_socket.recv(1024).decode()
                if not data:
                    break
                if data == "GET_TABLES":
                    self.send_tables_structure(client_socket)
                else:
                    self.process_query(client_socket, data)
        except Exception as e:
            self.logger.log(f"Error with {addr}: {str(e)}")
        finally:
            client_socket.close()
            self.logger.log(f"Connection closed with {addr}")

    def send_tables_structure(self, client_socket):
        structure = {}
        for table_name in os.listdir(self.tables_dir):
            table_path = os.path.join(self.tables_dir, table_name, "data.csv")
            if os.path.exists(table_path):
                with open(table_path, "r", encoding='utf-8-sig') as f:
                    reader = csv.reader(f)
                    headers = next(reader, [])
                    structure[table_name] = headers
        client_socket.send(json.dumps(structure).encode('utf-8'))

    def process_query(self, client_socket, query):
        cache_key = query
        cached_result = self.cache.get(cache_key)
        if cached_result:
            print(f"Sending cached result: {cached_result}")
            client_socket.send(cached_result.encode('utf-8'))
            self.logger.log(f"Returned cached result for query: {query}")
            return

        try:
            parsed = parse_sql(query)
            if parsed["type"] != "SELECT":
                client_socket.send("Only SELECT queries are supported".encode('utf-8'))
                return

            table_name = parsed["table"]
            table_path = os.path.join(self.tables_dir, table_name, "data.csv")
            print(f"Looking for table at: {table_path}")
            if not os.path.exists(table_path):
                client_socket.send(f"Table {table_name} not found".encode('utf-8'))
                return

            # Создаём временный файл
            temp_file = NamedTemporaryFile(mode="w+", delete=False, suffix=".csv", encoding='utf-8')
            temp_file_name = temp_file.name

            try:
                # Читаем исходный CSV и пишем во временный
                with open(table_path, "r", encoding='utf-8-sig') as f:
                    reader = csv.DictReader(f)
                    fieldnames = reader.fieldnames
                    print(f"Fieldnames: {fieldnames}")
                    writer = csv.DictWriter(temp_file, fieldnames=fieldnames)
                    writer.writeheader()

                    rows_written = 0
                    for row in reader:
                        print(f"Processing row: {row}")
                        if self.evaluate_where(row, parsed.get("where")):
                            writer.writerow(row)
                            rows_written += 1
                    print(f"Rows written to temp file: {rows_written}")

                # Закрываем временный файл
                temp_file.flush()
                temp_file.close()

                # Читаем результат
                with open(temp_file_name, "r", encoding='utf-8') as f:
                    result = f.read()
                    print(f"Sending result:\n{result}")
                    print(f"Sending {len(result)} characters")
                    if not result.strip():
                        client_socket.send("No data found".encode('utf-8'))
                    else:
                        client_socket.send(result.encode('utf-8'))
                        self.cache.set(cache_key, result)
                    self.logger.log(f"Processed query: {query}")

            finally:
                # Безопасно удаляем временный файл
                try:
                    if os.path.exists(temp_file_name):
                        os.unlink(temp_file_name)
                except Exception as e:
                    print(f"Warning: Could not delete temp file {temp_file_name}: {str(e)}")
                    self.logger.log(f"Warning: Could not delete temp file {temp_file_name}: {str(e)}")

        except Exception as e:
            error_msg = f"Error processing query: {str(e)}"
            client_socket.send(error_msg.encode('utf-8'))
            self.logger.log(f"Query error: {str(e)}")

    def evaluate_where(self, row, where):
        if not where:
            return True
        column, operator, value = where
        row_value = row.get(column)
        if row_value is None:
            return False

        # Проверяем, является ли значение числом
        try:
            row_value = float(row_value)
            value = float(value)
        except (ValueError, TypeError):
            # Если не число, сравниваем как строки
            row_value = str(row_value)
            value = str(value)

        print(f"Evaluating: {column} {operator} {value} (row_value: {row_value})")  # Отладка

        if operator == "=":
            return row_value == value
        elif operator == "<":
            return row_value < value
        elif operator == ">":
            return row_value > value
        elif operator == "<=":
            return row_value <= value
        elif operator == ">=":
            return row_value >= value
        elif operator == "!=":
            return row_value != value
        return False

def run_server():
    server = Server()
    server.run()