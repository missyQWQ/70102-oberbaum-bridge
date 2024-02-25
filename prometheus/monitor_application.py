from prometheus_client import start_http_server, Counter
import time


def start_server(port):
    start_http_server(port)


class PrometheusMonitor:

    def __init__(self, port=8000):
        start_server(port)
        self.messages_received = Counter('messages_received_total', 'Total number of messages received')
        self.ages_sent = Counter('pages_sent_total', 'Total number of pages sent')


