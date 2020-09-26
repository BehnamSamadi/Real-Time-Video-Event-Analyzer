"""
This module manages streams, decoding, fetching and classification pipeline
"""
from stream import Stream


class StreamManager(object):
    def __init__(self, streams, queue):
        self.queue = queue
        self.decoders = dict()
        for s in streams:
            self.add_new_stream(s)

    def add_new_stream(self, stream_prop):
        self.remove_stream(stream_prop['id'])
        dcr = Stream()
        dcr.apply_async(stream_prop['id'], stream_prop['address'],
                        self.queue, stream_prop['sample_duration'],
                        stream_prop['sample_size'], stream_prop['frame_size'],
                        stream_prop['active_delay'], stream_prop['sensitivity'])
        self.decoders[stream_prop['id']] = dcr

    def remove_stream(self, stream_id):
        if stream_id in self.decoders.keys():
            dcr = self.decoders[stream_id]
            dcr.CAPTURE_FLAG = False
            self.decoders.pop(stream_id, None)
            return True
        return False
