from prometheus_client import Counter, start_http_server, Histogram

messages_received = Counter('messages_received_total', 'Total number of messages received')
pages_sent = Counter('pages_sent_total', 'Total number of pages sent')
tests_received = Counter('tests_received_total', 'Total number of tests received')
positive_detection = Counter('positive_detection_total', 'Total number of positive detections')
http_error_received = Counter('http_error_recieved_total', 'Total number of http error received')
reconnection_detection = Counter('reconnection_detection_total', 'Total number of reconnection')
results_distribution = Histogram('results_distribution', 'Distribution of results')