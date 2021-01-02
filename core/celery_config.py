import os

name= 'Core'
broker = 'amqp://localhost'
# broker = os.getenv('SP_BROKER_URL', 'amqp://localhost')
result_backend = 'redis://localhost:6379/0'
timezone = 'Asia/Tehran'
enable_utc = True
result_backend_transport_options = {'visibility_timeout': 18000}

task_routes = {
    'core.*': {'queue': 'core'},
    'backend.*': {'queue': 'backend'},
    'decoder.*': {'queue': 'decoder'},
}