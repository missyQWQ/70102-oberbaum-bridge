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

    def get_history(self):
        return self.history

    def set_history(self, history):
        self.history = history

    def set_admitted_patient(self, admitted_patient):
        self.admitted_patient = admitted_patient

    def set_discharged_patient(self, discharged_patient):
        self.discharged_patient = discharged_patient

    def set_creatine_results(self, creatine_results):
        self.creatine_results = creatine_results

    def set_paged_patient(self, paged_patient):
        self.paged_patient = paged_patient

    def get_admitted_patient(self):
        return self.admitted_patient

    def get_discharged_patient(self):
        return self.discharged_patient

    def get_creatine_results(self):
        return self.creatine_results

    def get_paged_patient(self):
        return self.paged_patient
