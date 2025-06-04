from app.celery import app as celery_app
from app.cruds.task import update_task_status
from sqlalchemy.orm import Session
from app.db.base import get_db
import requests
from bs4 import BeautifulSoup
import networkx as nx
import time
from datetime import datetime
import redis
import json

@celery_app.task(bind=True)
def parse_website(self, url: str, max_depth: int, user_id: int, task_id: str):
    print(f"[DEBUG] Задача получена: task_id={task_id}, url={url}, user_id={user_id}, max_depth={max_depth}, time: {time.ctime()}")
    try:
        db = next(get_db())
        client_id = str(user_id)
        start_time = datetime.utcnow()

        # Подключение к Redis для отправки сообщений
        redis_client = redis.Redis(host='localhost', port=6379, db=0)

        print(f"[DEBUG] Запуск задачи для client_id={client_id}, task_id={task_id}, time: {time.ctime()}")
        update_task_status(db, task_id, "STARTED")
        message = {
            "status": "STARTED",
            "task_id": task_id,
            "url": url,
            "max_depth": max_depth,
            "time": time.ctime()
        }
        redis_client.publish(f"ws_{client_id}", json.dumps(message))
        print(f"[DEBUG] Published to Redis channel ws_{client_id}: {message}, time: {time.ctime()}")

        graph = nx.DiGraph()
        visited = set()
        pages_to_parse = [(url, 0)]
        pages_parsed = 0
        total_pages = 10
        links_found = 0

        while pages_to_parse and pages_parsed < total_pages:
            current_url, depth = pages_to_parse.pop(0)
            if current_url in visited or depth > max_depth:
                continue

            try:
                print(f"[DEBUG] Парсинг URL: {current_url}, глубина: {depth}, time: {time.ctime()}")
                response = requests.get(current_url, timeout=5)
                soup = BeautifulSoup(response.text, 'html.parser')
                visited.add(current_url)
                pages_parsed += 1
                graph.add_node(current_url)

                links = [a.get('href') for a in soup.find_all('a', href=True) if a.get('href').startswith('http')]
                links_found += len(links)
                for link in links[:5]:
                    graph.add_edge(current_url, link)
                    if link not in visited:
                        pages_to_parse.append((link, depth + 1))

                progress = int((pages_parsed / total_pages) * 100)
                update_task_status(db, task_id, "PROGRESS")
                message = {
                    "status": "PROGRESS",
                    "task_id": task_id,
                    "progress": progress,
                    "current_url": current_url,
                    "pages_parsed": pages_parsed,
                    "total_pages": total_pages,
                    "links_found": links_found,
                    "time": time.ctime()
                }
                redis_client.publish(f"ws_{client_id}", json.dumps(message))
                print(f"[DEBUG] Published to Redis channel ws_{client_id}: {message}, time: {time.ctime()}")
                time.sleep(1)

            except Exception as e:
                print(f"[DEBUG] Ошибка при парсинге {current_url}: {e}, time: {time.ctime()}")
                continue

        graphml_file = f"/Users/polinazharkova/Desktop/учеба/Практикум/graph_{task_id}.graphml"
        print(f"[DEBUG] Сохранение GraphML-файла: {graphml_file}, time: {time.ctime()}")
        nx.write_graphml(graph, graphml_file)

        elapsed_time = str(datetime.utcnow() - start_time)
        update_task_status(db, task_id, "COMPLETED")
        message = {
            "status": "COMPLETED",
            "task_id": task_id,
            "total_pages": pages_parsed,
            "total_links": links_found,
            "elapsed_time": elapsed_time,
            "result": f"Graph saved to {graphml_file}",
            "time": time.ctime()
        }
        redis_client.publish(f"ws_{client_id}", json.dumps(message))
        print(f"[DEBUG] Published to Redis channel ws_{client_id}: {message}, time: {time.ctime()}")

        db.close()
        redis_client.close()
        print(f"[DEBUG] Задача завершена для client_id={client_id}, task_id={task_id}, time: {time.ctime()}")
    except Exception as e:
        print(f"[DEBUG] Ошибка в задаче: {e}, time: {time.ctime()}")
        raise e