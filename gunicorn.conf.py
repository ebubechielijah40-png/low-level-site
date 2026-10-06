"""Linux WSGI service behind the existing tunnel or a trusted HTTPS proxy."""
import os
bind=os.environ.get('GUNICORN_BIND','127.0.0.1:8000')
workers=int(os.environ.get('WEB_CONCURRENCY','2'))
worker_class='sync'
threads=1
timeout=15
graceful_timeout=15
max_requests=1000
max_requests_jitter=100
accesslog=None
errorlog='-'
capture_output=True
forwarded_allow_ips=os.environ.get('FORWARDED_ALLOW_IPS','127.0.0.1,::1')
control_socket_disable=True
