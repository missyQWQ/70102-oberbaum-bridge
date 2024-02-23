import os
import pandas as pd
import numpy as np


class DataProvider:
    def __init__(self):
        self.history = None
        self.admitted_patient = {}
        self.discharged_patient = []
        self.creatine_results = {}
        self.paged_patient = []
        self.positive_detect = 0
        self.negative_detect = 0
        self.request_count = 0
        self.confusion_matrix = {'TP': 0, 'FP': 0, 'TN': 0, 'FN': 0}
        self.message_count = 0
        self.test_count = 0
        self.http_error_count = 0
        self.reconnection_error_count = 0
        self.test_results = []

    def get_history(self):
        return self.history

    def set_history(self, history):
        self.history = history.copy()

    def set_admitted_patient(self, admitted_patient):
        self.admitted_patient = admitted_patient

    def set_discharged_patient(self, discharged_patient):
        self.discharged_patient = discharged_patient

    def set_creatine_results(self, creatine_results):
        self.creatine_results = creatine_results

    def set_paged_patient(self, paged_patient):
        self.paged_patient.append(paged_patient)

    def get_admitted_patient(self):
        return self.admitted_patient

    def get_discharged_patient(self):
        return self.discharged_patient

    def get_creatine_results(self):
        return self.creatine_results

    def get_paged_patient(self):
        return self.paged_patient

    def get_request_count(self):
        return self.request_count

    def get_confusion_matrix(self):
        return self.confusion_matrix

    def get_message_count(self):
        return self.message_count

    def get_test_count(self):
        return self.test_count

    def get_http_error_count(self):
        return self.http_error_count

    def get_reconnection_error_count(self):
        return self.reconnection_error_count

    def get_test_results(self):
        percentile_25 = np.percentile(self.test_results, 25)
        median = np.percentile(self.test_results, 50)
        percentile_75 = np.percentile(self.test_results, 75)
        return percentile_25, median, percentile_75