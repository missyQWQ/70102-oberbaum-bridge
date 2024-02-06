import aiohttp
import asyncio


async def run_http_pager(pager):
    await pager.open_session()


async def close_http_pager(pager):
    await pager.close_session()


async def parse_patients(pager, result):
    await pager.parse(result)

class Pager:
    def __init__(self, url='localhost:8441/page'):
        self.url = url
        self.session = None
        print("Pager constructed...")

    async def open_session(self):
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
            print("Session Opened!")
        else:
            print("Session Already Opened!")

    async def close_session(self):
        if self.session is not None and not self.session.closed:
            await self.session.close()
            print("Session Closed!")
        else:
            print("Session Already Closed? Is this expected???")

    async def parse(self, res):
        (MRN, label) = res
        if label == 'y':
            try:
                mrn_int = int(MRN)
            except Exception as e:
                print(f"Unidentified MRN:{MRN}")
                raise Exception("Pager: Probably broken data?")
            print(f"AKI detected for {MRN}, send message to pager.")
            await self.post(str(MRN))

        elif label != 'n':
            print("Pager: Probably broken data?")
            raise Exception(f"Unidentified label:{label}")

    async def post(self, data):
        try:
            async with self.session.post(self.url, data=data) as response:
                # Check Response!
                if response.status == 200:
                    print(f"Pager: success: {response.status} for data {data}")
                    return await response.text()
                else:
                    print(f"Error: server returns {response.status} for data {data}")
                    return None
        except Exception as e:
            print(e)
            print("Pager: network error")
