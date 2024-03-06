import aiohttp
import asyncio
from datetime import datetime
from monitor_application import pages_sent, http_error_received
from log_provider import get_logger


# Wrap functions for dataloader module
async def run_http_pager(pager):
    await pager.open_session()


async def close_http_pager(pager):
    await pager.close_session()


async def parse_patients(pager, result):
    await pager.parse(result)


# The pager class
class Pager:
    # @params
    # url: the url link to the pager simulator.
    def __init__(self, url="http://localhost:8441/page"):
        self.url = url
        self.session = None
        get_logger(__name__).info(f"Pager constructed...")
        print("Pager constructed...")

    # Open a TCP session
    async def open_session(self):
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
            # print("Session Opened!")
        else:
            print("Session Already Opened!")

    # Close a TCP session
    async def close_session(self):
        if self.session is not None and not self.session.closed:
            await self.session.close()
            # print("Session Closed!")
        else:
            print("Session Already Closed? Is this expected???")

    # parse the model output
    async def parse(self, res):
        (MRN, time_str, label) = res
        # timestamp of receive the result
        timestamp = None
        if label == 'y':
            try:
                # check if the MRN is the format of int, otherwise, throw exception.
                mrn_int = int(MRN)
                # convert the timestamp to the right format.
                time_obj = datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')
                timestamp = time_obj.strftime('%Y%m%d%H%M')
            except Exception as e:
                # MRN is not the correct format.
                raise ValueError("Pager: Probably broken data?")
            # Sends a message to the pager simulator.
            await self.post(str(MRN) + "," + timestamp)

        elif label != 'n':
            # received a malformed label
            raise ValueError(f"Unidentified label:{label}")

    # Do POST
    async def post(self, data):
        try:
            async with self.session.post(self.url, data=data) as response:
                # Check Response!
                if response.status == 200:
                    # Page successfully send, increase prometheus counter.
                    pages_sent.inc()
                    # Produce a log
                    get_logger(__name__).info(f"Pager: success: {response.status} for data {data}")
                    print(f"Pager: success: {response.status} for data {data}")
                    return await response.text()
                else:
                    # Network err
                    http_error_received.inc()
                    raise IOError(f"SERVER_SIDE ERR: {response.status}")

        except Exception as e:
            raise IOError(f"Network error:{e}")

