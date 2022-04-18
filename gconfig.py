from multiprocessing import cpu_count

bind = '0.0.0.0:8080'

workers = (2 * cpu_count()) + 1
worker_class = 'gevent'
worker_connections = 1000

timeout = 60