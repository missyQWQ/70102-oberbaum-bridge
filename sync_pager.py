import requests


class Pager:
    def __init__(self, url="http://localhost:8441/page"):
        self.url = url
        self.session = None
        print("Pager constructed...")

    def open_session(self):
        if self.session is None or self.session.closed:
            self.session = requests.Session()
            print("Session Opened!")
        else:
            print("Session Already Opened!")

    def close_session(self):
        if self.session is not None:
            pass

    def parse(self, res):
        (MRN, label) = res
        if label == 'y':
            try:
                mrn_int = int(MRN)
            except Exception as e:
                print(e)
                print(f"Unidentified MRN:{MRN}")
                raise Exception("Pager: Probably broken data?")
            print(f"AKI detected for {MRN}, send message to pager.")
            self.post(str(mrn_int))

        elif label != 'n':
            print("Pager: Probably broken data?")
            raise Exception(f"Unidentified label:{label}")

    def post(self, data):
        try:
            response = self.session.post(self.url, data=data)
            # Check Response!
            if response.status_code == 200:
                print(f"Pager: success: {response.status_code} for data {data}")
                return response.text
            else:
                print(f"Error: server returns {response.status_code} for data {data}")
                return None
        except Exception as e:
            print(e)
            print("Pager: network error")


def run_http_pager(pager):
    pager.open_session()


def close_http_pager(pager):
    pager.close_session()


def parse_patients(pager, result):
    pager.parse(result)
