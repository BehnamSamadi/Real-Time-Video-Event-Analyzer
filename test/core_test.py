from celery import Celery


app = Celery(name='Core_test')
app.conf.task_routes = {
    'core.*': {'queue': 'core'},
    'backend.*': {'queue': 'backend'},
    'decoder.*': {'queue': 'decoder'},
}

app.config_from_object('celery_config')


res = app.send_task('core.update_ml')


