import aiohttp
import asyncio


class Pager:
    def __init__(self, url='localhost:8441/page'):
        self.url = url
        self.session = None
        self.open_session()
        print("Pager loaded...")

    async def open_session(self):
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()

    async def close_session(self):
        if self.session is not None and not self.session.closed:
            await self.session.close()

    async def parse(self, res):
        try:
            (MRN, label) = res
            if label == 'y':
                print(f"AKI detected for {MRN}, send message to pager.")
                self.post(int(MRN))
        except:
            print("Pager: Probably broken data?")

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
        except:
            print("Pager: network error")

    def __del__(self):
        self.close_session()
        print("Pager connection closed")
