"""
This module manages streams, decoding, fetching and classification pipeline
"""
from stream import Stream


class StreamManager(object):
    def __init__(self, streams, queue):
        self.queue = queue
        self.decoders = dict()
        for s in streams:
            dcr = Stream(s.address, self.queue)
            self.decoders[s.id] = dcr

    def add_new_stream(self, stream):
        dcr = Stream(stream.address, self.queue)
        self.decoders[stream.id] = dcr

    def remove_stream(self, stream_id):
        return self.decoders.pop(stream_id, None)

    def run(self):
        pass



