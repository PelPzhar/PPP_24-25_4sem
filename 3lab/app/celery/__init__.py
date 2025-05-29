from celery import Celery
import redislite

redis_instance = redislite.Redis()
socket_file = redis_instance.socket_file
broker_url = f"redis+socket://{socket_file}"
backend_url = f"redis+socket://{socket_file}"

app = Celery(
    'tasks',
    broker=broker_url,
    backend=backend_url
)

app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

app.autodiscover_tasks(['app.celery'])