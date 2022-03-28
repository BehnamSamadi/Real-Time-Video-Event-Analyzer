from celery import Celery
import time

app = Celery('Decoder_test')
app.conf.task_routes = {
    'core.*': {'queue': 'core'},
    'backend.*': {'queue': 'backend'},
    'decoder.*': {'queue': 'decoder'},
}

app.config_from_object('celery_config')

stream_prop = {
    'id': '0',
    'address': 'rtsp://localhost:8554/sample.265',
    'sample_duration': 3.2,
    'sample_size': 32,
    'frame_size': (256, 256),
    'active_delay': 1.6,
    'sensitivity': 0.0
}


app.send_task('decoder.add_stream', (stream_prop,))
# # time.sleep(6)
# app.send_task('decoder.remove_stream', ('0',))