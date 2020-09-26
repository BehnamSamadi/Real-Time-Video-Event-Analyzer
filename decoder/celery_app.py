from celery import Celery


app = Celery()
app.config_from_object('celery_config')