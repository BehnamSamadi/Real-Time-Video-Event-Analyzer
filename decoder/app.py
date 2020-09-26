from celery_app import app
from stream_manager import StreamManager
from utils import fetch_streams
import redis


streams = fetch_streams()
queue_name = 'queue:clips'
stream_mgr = StreamManager(streams, queue_name)


@app.task(name='decoder.add_stream')
def add_stream(stream_prop):
    stream_mgr.add_new_stream(stream_prop)

@app.task(name='decoder.remove_stream')
def remove_stream(stream_id):
    stream_mgr.remove_stream(stream_id)

