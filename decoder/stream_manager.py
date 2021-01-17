"""
This module manages streams, decoding, fetching and classification pipeline
"""
from stream import Stream
import redis
import time


class StreamManager(object):
    def __init__(self, app, streams, queue_name):
        self.app = app
        self.queue_name = queue_name
        self.decoders = dict()
        self.redis_db = redis.Redis(db=1)
        for s in streams:
            self.add_new_stream(s)

    def add_new_stream(self, stream_prop):
        self.remove_stream(stream_prop['id'])
        task_args = (stream_prop['id'], stream_prop['address'],
                        self.queue_name, stream_prop['sample_duration'],
                        stream_prop['sample_size'], stream_prop['frame_size'],
                        stream_prop['active_delay'], stream_prop['sensitivity'])
        dcr = Stream()
        result = dcr.apply_async(task_args, queue='decoder')
        self.decoders[stream_prop['id']] = {
                                            'task_object': dcr,
                                            'result': result
                                        }

    def remove_stream(self, stream_id):
        if stream_id in self.decoders.keys():
            self.redis_db.set(stream_id, 0)
            self.decoders.pop(stream_id, None)
            return True
        return False
