class Metrics():
    def __init__(self, positive_detect, negative_detect, request, negative_score):
        self.positive_detect = 0
        self.negative_detect = 0
        self.request_count = 0
        self.confusion_matrix = {'TP': 0, 'FP': 0, 'TN': 0, 'FN': 0}