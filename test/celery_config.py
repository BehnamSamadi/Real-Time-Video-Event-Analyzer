name= 'Decoder'
broker = 'amqp://localhost'
# broker = 'redis://localhost:6379/0'
result_backend = 'redis://localhost:6379/0'
timezone = 'Asia/Tehran'
enable_utc = True
result_backend_transport_options = {'visibility_timeout': 18000}