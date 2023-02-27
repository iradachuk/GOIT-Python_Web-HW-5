import asyncio
import argparse
import platform
import logging

from datetime import datetime, timedelta

import aiohttp


parser = argparse.ArgumentParser(description='App for getting exchange rate')
parser.add_argument('-d', '--days', default='1', required=True)
args = vars(parser.parse_args())
days = int(args.get('days'))


async def request(url):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    r = await response.json()
                    return r
                logging.error(f'Error status: {response.status} for {url}')
        except aiohttp.ClientConnectorError as e:
            logging.error(f'Connection error {url}: {e}')
        return None


async def get_exchange(days):
    if days > 10:
        days = 10
    dates = [(datetime.now()-timedelta(days=d)).strftime('%d.%m.%Y')
             for d in range(days)]
    exchange_rate = [request(
        f'https://api.privatbank.ua/p24api/exchange_rates?json&date={date}') for date in dates]
    result = await asyncio.gather(*exchange_rate)
    for res in result:
        if res:
            parse_currency(res)


def parse_currency(rate):
    date = rate['date']
    print(f'\n{date}:')
    for r in rate['exchangeRate']:
        if r['currency'] in ['USD', 'EUR']:
            print(
                f'{r["currency"]}: sale: {r["saleRate"]}, buy: {r["purchaseRate"]}')


if __name__ == "__main__":
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    r = asyncio.run(get_exchange(days))
    print(r)
