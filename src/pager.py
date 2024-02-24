import aiohttp
import asyncio
from datetime import datetime
from monitor_application import pages_sent, http_error_received
from src.log_provider import get_logger


async def run_http_pager(pager):
    await pager.open_session()


async def close_http_pager(pager):
    await pager.close_session()


async def parse_patients(pager, result):
    await pager.parse(result)


class Pager:
    def __init__(self, url="http://localhost:8441/page"):
        self.url = url
        self.session = None
        get_logger(__name__).info(f"Pager constructed...")
        print("Pager constructed...")

    async def open_session(self):
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
            # print("Session Opened!")
        else:
            print("Session Already Opened!")

    async def close_session(self):
        if self.session is not None and not self.session.closed:
            await self.session.close()
            # print("Session Closed!")
        else:
            print("Session Already Closed? Is this expected???")

    async def parse(self, res):
        (MRN, time_str, label) = res
        timestamp = None
        if label == 'y':
            try:
                mrn_int = int(MRN)
                time_obj = datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')
                timestamp = time_obj.strftime('%Y%m%d%H%M')
            except Exception as e:
                raise ValueError("Pager: Probably broken data?")
            await self.post(str(MRN) + "," + timestamp)

        elif label != 'n':
            raise ValueError(f"Unidentified label:{label}")

    async def post(self, data):
        try:
            async with self.session.post(self.url, data=data) as response:
                # Check Response!
                if response.status == 200:
                    pages_sent.inc()
                    get_logger(__name__).info(f"Pager: success: {response.status} for data {data}")
                    print(f"Pager: success: {response.status} for data {data}")
                    return await response.text()
                else:
                    http_error_received.inc()
                    raise IOError(f"SERVER_SIDE ERR: {response.status}")

        except Exception as e:
            raise IOError(f"Network error:{e}")

