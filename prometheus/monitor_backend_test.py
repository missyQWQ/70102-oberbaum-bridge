from prometheus_client import start_http_server, Counter
import time

messages_received = Counter('messages_received_total', 'Total number of messages received')
pages_sent = Counter('pages_sent_total', 'Total number of pages sent')


def process_requests():
    while True:
        messages_received.inc()
        pages_sent.inc()
        time.sleep(2)


if __name__ == '__main__':
    start_http_server(8440)
    print("Metrics server started on port 8440.")
    process_requests()
