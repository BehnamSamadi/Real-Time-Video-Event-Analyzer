from celery import Celery


app = Celery(name='Core_test')

app.send_task('core.update_ml')


