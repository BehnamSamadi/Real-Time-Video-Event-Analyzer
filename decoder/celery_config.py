name= 'Decoder'
broker = os.getenv('CELERY_BROKER', 'amqp://localhost')
# broker = os.getenv('SP_BROKER_URL', 'amqp://localhost')
timezone = 'Asia/Tehran'
enable_utc = True
result_backend_transport_options = {'visibility_timeout': 18000}

task_routes = {
    'core.*': {'queue': 'core'},
    'backend.*': {'queue': 'backend'},
    'decoder.*': {'queue': 'decoder'},
}