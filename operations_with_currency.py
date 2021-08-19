import pandas
import requests
from matplotlib import pyplot
from constants import API_KEY, HOST, ENDPOINT_EXCHANGE_RATE
from db_queries import insert, update, select
from datetime import datetime, timedelta, date
import psycopg2


def get_all_currencies():
    """Request to get list of currencies"""
    response = requests.get(f'{HOST}apicurrencies', params={'api_key': API_KEY})
    content = response.json()
    currencies = content.get('currencies', [])
    list_of_currencies = [currency for currency in currencies]
    list_of_currencies = ','.join(list_of_currencies)

    return list_of_currencies


def get_latest_exchange_rate(now=datetime.now()):
    """
    Receive exchange rate of all currencies
    If last request was 10 or mor minutes ago, exchange rates will be taken from web sercive
    Otherwise, information will be taken from database
    """
    try:
        last_request_time = select(1)[0]
        interval = (now - last_request_time[0]).seconds
        if (interval / 60) >= 10:
            return exchange_rate_from_service()
        else:
            return exchange_rate_from_db()
    except TypeError:
        return exchange_rate_from_service()


def exchange_rate_from_service():
    response = requests.get(f'{HOST}{ENDPOINT_EXCHANGE_RATE}',
                            params={'api_key': API_KEY, 'currency': get_all_currencies()})
    content = response.json()

    currencies_info = content.get('price', [])
    save_currency_to_db(currencies_info)

    return currencies_info


def exchange_rate_from_db():
    currency_from_db = select()
    return currency_from_db


def save_currency_to_db(currencies):
    """Saves currency to local database"""
    rows = [("{:.2f}".format(exchange_rate), datetime.now(), name) for name, exchange_rate in currencies.items()]
    try:
        insert(rows)
    except (Exception, psycopg2.Error):
        update(rows)


def make_currency_list():
    """Unpack dict with currencies and exchange rates in readable from"""
    currencies = get_latest_exchange_rate()

    if type(currencies) is list:
        currency_list = currencies[:]
        currencies = {}

        for currency in currency_list:
            currencies[currency[0]] = float(currency[1])

    currency_info = [f'{name.replace("USD", "")} : {exchange_rate:.2f}' for name, exchange_rate in currencies.items()]
    name_and_rate = '\n'.join(currency_info)
    return name_and_rate


def exchange_currency(currency_to_exchange, amount):
    """Exchange USD to any availble currency"""
    if 'USD' in currency_to_exchange:
        currency_to_exchange = currency_to_exchange.replace('USD', '')

    response = requests.get(f'{HOST}{"apiconvert"}',
                            params={'api_key': API_KEY,
                                    'from': 'USD',
                                    'to': currency_to_exchange,
                                    'amount': amount
                                    })

    content = response.json()
    exchanged_amount = content.get('total', [])
    if not exchanged_amount:
        return 'Invalid currency'
    return f'{exchanged_amount:.2f} {currency_to_exchange}'


def currency_graph_builder(currency, photo_id, end_date=date.today()):
    """"""
    url = f'{HOST}apipandas' \
          f'?api_key={API_KEY}' \
          f'&currency={currency}' \
          f'&start_date={end_date - timedelta(days=7)}' \
          f'&end_date={end_date}'
    try:
        currency_graph = pandas.read_json(url)
        currency_graph.plot()
        pyplot.savefig(f'{photo_id}')
        return f'{photo_id}'

    except TypeError:
        return 'No exchange rate data is available for the selected currency'

