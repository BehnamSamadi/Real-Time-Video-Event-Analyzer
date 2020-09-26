from celery import Celery
from stream_manager import StreamManager
from utils import fetch_streams
import redis


app = Celery()
app.config_from_object('celery_config')
streams = fetch_streams()
queue = redis.Redis()
stream_mgr = StreamManager(streams, queue)


@app.task(name='decoder.add_stream')
def add_stream(stream_prop):
    stream_mgr.add_new_stream(stream_prop)

@app.task(name='decoder.remove_stream')
def remove_stream(stream_id):
    stream_mgr.remove_stream(stream_id)

