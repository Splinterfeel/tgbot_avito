import asyncio
import aiohttp
from io import BytesIO
import pandas as pd
from aioresponses import aioresponses


class AvitoAPIClient:
    URL_GET_AD_STATS = 'https://api.avito.ru/core/v1/accounts/{user_id}/calls/stats/'
    URL_GET_ADS = 'https://api.avito.ru/core/v1/items/'
    URL_AUTH = 'https://api.avito.ru/token/'

    def __init__(self, client_id: str = None, client_secret: str = None) -> None:
        self.loop = asyncio.get_event_loop()
        self.client_id = client_id
        self.client_secret = client_secret
        self.auth_success = False
        self.advertisments = dict()
        self.headers = {'Authorization': None, 'Content-Type': 'application/json'}

    @aioresponses()
    async def auth(self, mocked) -> None:
        mocked.post(self.URL_AUTH, payload={
                "access_token": "kChqt9ewQNAcwgbHp4yFd5",
                "expires_in": 86400,
                "token_type": "Bearer"
        })
        async with aiohttp.ClientSession() as session:
            async with session.post(self.URL_AUTH) as resp:
                resp_json = await resp.json()
                self.access_token = resp_json['access_token']
                self.headers['Authorization'] = 'Bearer' + self.access_token
                self.auth_success = True

    @aioresponses()
    async def get_advertisments(self, mocked):
        mocked.get(self.URL_GET_ADS, status=200, payload={
                "meta": {
                    "page": 1,
                    "per_page": 25
                },
                "resources": [
                    {
                        "address": "Москва, Лесная улица 7",
                        "category": {},
                        "id": 24122231,
                        "price": 35000,
                        "status": "active",
                        "title": "Продавец-кассир",
                        "url": "https://www.avito.ru/rostov-na-donu/vakansii/prodavets_magazina_2142"
                    }
                ]
        })
        if not self.auth_success:
            raise ValueError('No auth!')
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(self.URL_GET_ADS) as resp:
                resp_data = await resp.json()
                self.URL_GET_AD_STATS = self.URL_GET_AD_STATS.replace('{user_id}', str(self.client_id))
                self.advertisments = {a['id']: a for a in resp_data['resources']}

    async def gather_advertisments_stats(self) -> None:
        requests_tasks = []
        for adv_id in self.advertisments:
            task = asyncio.create_task(self.__get_advertisment_stats(adv_id))
            requests_tasks.append(task)
        await asyncio.gather(*requests_tasks)

    @aioresponses()
    async def __get_advertisment_stats(self, adv_id, mocked) -> None:
        if not self.auth_success:
            raise ValueError('No auth!')
        mocked.post(self.URL_GET_AD_STATS + str(adv_id) + f"?user_id={self.client_id}", status=200,
                        payload={
                            "result": {
                                "items": [{
                                    "days": [{
                                        "answered": 0,
                                        "calls": 0,
                                        "date": "2020-04-01",
                                        "new": 0,
                                        "newAnswered": 0
                                        }
                                    ],
                                    "employeeId": 0,
                                    "itemId": 1853257996
                                    }
                                ]
                            }
                        })
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.post(self.URL_GET_AD_STATS + str(adv_id), params={'user_id': self.client_id},
                                    json={
                                        'dateFrom': '2024-01-01',
                                        'dateTo': '2024-12-31',
                                        'itemIds': [adv_id]}) as resp:
                resp_json = await resp.json()
                self.advertisments[adv_id]['stats'] = resp_json['result']['items'][0]

    def form_report_file(self) -> BytesIO:
        if not self.advertisments:
            raise ValueError('No advertisments!')
        csv_data = []
        csv_headers = ['answered', 'calls', 'new', 'newAnswered']
        for advertisment_id, advertisment_data in self.advertisments.items():
            adv_info = {'advertisment_id': advertisment_id}
            for column in csv_headers:
                adv_info[column] = sum(i[column] for i in advertisment_data['stats']['days'])
            csv_data.append(adv_info)
        csv_headers.insert(0, 'advertisment_id')
        bytes_file = BytesIO()
        writer = pd.ExcelWriter(bytes_file, engine='xlsxwriter')
        df = pd.DataFrame.from_dict(csv_data, orient='columns')
        df.to_excel(writer, sheet_name='Sheet1', index=False)
        writer.close()
        bytes_file.seek(0)
        return bytes_file.getvalue()
