from celery import Celery
import requests

celery_app = Celery()
celery_app.config_from_object('celery_config')



@celery_app.task(name='backend.update_stream_status')
def update_stream_status(stream_status):
    res = requests.post('http://localhost:5000/update_status', json=stream_status)
    print(res)