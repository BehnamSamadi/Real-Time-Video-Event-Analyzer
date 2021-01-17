from celery_app import app
from stream_manager import StreamManager
from utils import fetch_streams
import redis


streams = fetch_streams()
queue_name = 'queue:clips'
stream_mgr = StreamManager(app, streams, queue_name)


@app.task(name='decoder.add_stream')
def add_stream(stream_prop):
    print('new stream recived')
    stream_mgr.add_new_stream(stream_prop)
    print('Stream: {} added'.format(stream_prop))

@app.task(name='decoder.remove_stream')
def remove_stream(stream_id):
    res = stream_mgr.remove_stream(stream_id)
    # print('stream {} {} removed'.format(stream_id, res))
    return res


