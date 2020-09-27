from celery import Celery


app = Celery('Decoder_test')

stream_prop = {
    'id': '0',
    'address': 'rtsp://localhost:8554/sed.mkv',
    'sample_duration': 5,
    'sample_size': 11,
    'frame_size': (320, 240),
    'active_delay': 2,
    'sensitivity': 0.0
}


app.send_task('decoder.add_stream', (stream_prop,))