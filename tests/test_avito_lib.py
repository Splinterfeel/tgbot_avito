import avito_lib
import pytest
from aioresponses import aioresponses


mock_advertisments = {
    24122231: {
        'address': 'Москва, Лесная улица 7', 'category': {},
        'id': 24122231, 'price': 35000, 'status': 'active',
        'title': 'Продавец-кассир', 'url': 'https://www.avito.ru/rostov-na-donu/vakansii/prodavets_magazina_2142'
        }
}

mock_stats = {
    'days': [
        {'answered': 0, 'calls': 0, 'date': '2020-04-01', 'new': 0, 'newAnswered': 0}
        ],
    'employeeId': 0, 'itemId': 1853257996
}


@pytest.mark.asyncio
@pytest.mark.avito
async def test_auth():
    @aioresponses()
    async def run(mocked: aioresponses) -> bool:
        avito_client = avito_lib.AvitoAPIClient(client_id=222, client_secret=12314)
        mocked.post(avito_client.URL_AUTH, payload={
                "access_token": "kChqt9ewQNAcwgbHp4yFd5",
                "expires_in": 86400,
                "token_type": "Bearer"
        })
        await avito_client.auth()
        return avito_client.auth_success
    assert await run()


@pytest.mark.asyncio
@pytest.mark.avito
async def test_advertisments():
    @aioresponses()
    async def run(mocked: aioresponses) -> bool:
        avito_client = avito_lib.AvitoAPIClient(client_id=222, client_secret=12314)
        mocked.post(avito_client.URL_AUTH, payload={
                "access_token": "kChqt9ewQNAcwgbHp4yFd5",
                "expires_in": 86400,
                "token_type": "Bearer"
        })
        mocked.get(avito_client.URL_GET_ADS, status=200, payload={
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
        await avito_client.auth()
        await avito_client.get_advertisments()
        return avito_client.advertisments
    assert mock_advertisments == await run()


@pytest.mark.asyncio
@pytest.mark.avito
async def test_stats():
    @aioresponses()
    async def run(mocked: aioresponses) -> bool:
        avito_client = avito_lib.AvitoAPIClient(client_id=222, client_secret=12314)
        mocked.post(avito_client.URL_AUTH, payload={
                "access_token": "kChqt9ewQNAcwgbHp4yFd5",
                "expires_in": 86400,
                "token_type": "Bearer"
        })
        mocked.get(avito_client.URL_GET_ADS, status=200, payload={
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
        await avito_client.auth()
        await avito_client.get_advertisments()
        for adv_id in avito_client.advertisments:
            mocked.post(avito_client.URL_GET_AD_STATS + str(adv_id) + f"?user_id={avito_client.client_id}", status=200,
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
        await avito_client.gather_advertisments_stats()
        return avito_client.advertisments
    assert mock_stats == (await run())[24122231]['stats']
