import time
import requests
from tradingview_ta import TA_Handler, Interval, Exchange
# from binance.um_futures import UMFutures #binance-futures-connector

from binance import Client, ThreadedWebsocketManager, ThreadedDepthCacheManager
from binance.client import Client

import pandas as pd
import copy

INTERVAL = Interval.INTERVAL_5_MINUTES  # желательно 4ч - или дневные для этой стратегии

TOKEN = '5886578012:AAHIPhYEMgf_UxqbLDR0v5NJc7XjY-0X5AI'
CHAT = '624736798'

KEY = '6ba95e7ed67fff7357a6a9fdca47e350852a2d62668d1db9570e5ae9db99e9c3'
SECRET = '793aebcbcff748c0350cd24979964541e28cbe8491e2005853c52bec0cd4473f'

client = Client(KEY, SECRET, tld='https://testnet.binancefuture.com', testnet=True)
stop_percent = 0.004
eth_proffit_array = [[2.2, 4], [3.5, 3.5], [5.5, 1.5], [7, 1], [80, 2], [150, 1], [200, 1], [200, 0]]
proffit_array = copy.copy(eth_proffit_array)
# парирумчик

def get_data(symbol):
    output = TA_Handler(symbol=symbol,  # даём на вход параметры
                        screener='Crypto',
                        exchange='Binance',
                        interval=INTERVAL)
    activiti = output.get_analysis().summary  # суммарный анализ по всем индикаторам
    activiti['SYMBOL'] = symbol  # добавляем символ чтобы собрать базу данных
    return activiti


def get_symbol():
    tickers = client.futures_mark_price()  # получаем рыночные цены
    symbols = []
    for i in tickers:
        ticker = i['symbol']  # из каждой монеты достаём символ
        symbols.append(ticker)  # помещаем в список
    return symbols


def send_message(text):
    res = requests.get('https://api.telegram.org/bot{}/sendMessage'.format(TOKEN), params=dict(
        chat_id=CHAT, text=text))


symbols = get_symbol()
longs = []
shorts = []


def first_data():  # выдаст готовые списки лонгов и шортов,в которых уже есть сигналы,но они не нужны
    print('Ищю данные')
    send_message('Ищу данные')
    for i in symbols:
        try:
            data = get_data(i)  # получаем данные о манетах
            # print(data)
            if (data['RECOMMENDATION'] == 'STRONG_BUY'):  # перебираем их
                longs.append(data['SYMBOL'])
                # print(data['SYMBOL'], 'Buy')
            if (data['RECOMMENDATION'] == 'STRONT_SELL'):
                shorts.append(data['SYMBOL'])
                # print(data['SYMBOL'], 'Short')
            time.sleep(0.01)  # чтобы избежать бана от трейдинг вью
        except:
            pass
    print('longs:')
    print(longs)
    print('shorts:')
    print(shorts)
    return longs, shorts


# ================================================================================
def open_position(symbol, s_l, quantity_l):
    #prt('open: ' + symbol + ' quantity: ' + str(quantity_l))
    sprice = get_symbol_price(symbol)

    if (s_l == 'long'):
        close_price = str(round(sprice * (1 + 0.01), 2))
        params = {
            "symbol": symbol,
            "side": "BUY",
            "type": "LIMIT",
            "quantity": str(quantity_l),
            "timeInForce": "GTC",
            "price": close_price

        }
        client.futures_create_order(**params)

    if (s_l == 'short'):
        close_price = str(round(sprice * (1 - 0.01), 2))
        params = {
            "symbol": symbol,
            "side": "SELL",
            "type": "LIMIT",
            "quantity": str(quantity_l),
            "timeInForce": "GTC",
            "price": close_price
        }
        client.futures_create_order(**params)


def close_position(symbol, s_l, quantity_l):
    #prt('close: ' + symbol + ' quantity: ' + str(quantity_l))
    sprice = get_symbol_price(symbol)

    if (s_l == 'long'):
        close_price = str(round(sprice * (1 - 0.01), 2))
        params = {
            "symbol": symbol,
            "side": "SELL",
            "type": "LIMIT",
            "quantity": str(quantity_l),
            "timeInForce": "GTC",
            "price": close_price
        }
        client.futures_create_order(**params)
    if (s_l == 'short'):
        close_price = str(round(sprice * (1 + 0.01), 2))
        params = {

            "symbol": symbol,
            "side": "BUY",
            "type": "LIMIT",
            "quantity": str(quantity_l),
            "timeInForce": "GTC",
            "price": close_price
        }
        client.futures_create_order(**params)


def get_symbol_price(symbol):
    prices = client.futures_mark_price()
    df = pd.DataFrame(prices)
    price= float(df[df['symbol'] == symbol]['markPrice'])
    return price


def get_profit_balance():  # профит и баланс
    status = client.futures_account()
    positions = pd.DataFrame(status['positions'])
    profit = float(status['totalUnrealizedProfit'])
    balance = round(float(status['totalWalletBalance']), 2)
    return ([profit, balance, 0])


def get_quanty_position(symbol):  # обьём монет в позиции
    status = client.futures_account()
    positions = pd.DataFrame(status['positions'])
    a = positions[positions['symbol'] == symbol]['positionAmt'].astype(float).tolist()[0]
    return ([a, 0])


def entry_price(symbol):  # цена входа в позицию
    status = client.futures_account()
    positions = pd.DataFrame(status['positions'])
    entryprice = positions[positions['symbol'] == symbol]['entryPrice']
    return ([round(float(entryprice), 3), 0])





def profit_and_stop_loss():
    try:
        for i in opened_position_long:
            temp_arr = copy.copy(proffit_array)
            symb_pr = get_symbol_price(i)
            stop_loss = entry_price(i) * (1 - stop_percent)
            entr_pr = entry_price(i)
            if symb_pr < stop_loss:
                close_position(symbol=i, s_l='BUY', quantity_l=abs(entr_pr))
                prt('===STOP_LOSS===')
                new_balans = get_profit_balance()[1]
            for j in range(0, len(temp_arr) - 1):
                maxpos = (my_balans // get_symbol_price(i)) // 10
                delta = temp_arr[j][0]
                contracts = temp_arr[j][1]
                if (symb_pr > (entr_pr + delta)):
                    close_position(symbol=i, s_l='BUY', quantity_l=
                    abs(round(maxpos * (contracts / 10), 3)))  # зарыть контракты из массива
                    new_balans = get_profit_balance()[1]
                    del proffit_array[0]
        if new_balans != 0:
            profit = new_balans - my_balans
            prt(str('Profit: ' + profit))
            prt(str('Balanse: ' + new_balans))
    except:
        pass
    try:
        for i in opened_position_short:
            temp_arr = copy.copy(proffit_array)
            symb_pr = get_symbol_price(i)
            stop_loss = entry_price(i) * (1 - stop_percent)
            entr_pr = entry_price(i)
            if symb_pr > stop_loss:
                close_position(symbol=i, s_l='SELL', quantity_l=abs(entr_pr))
                prt('===STOP_LOSS===')
                new_balans = get_profit_balance()[1]
            for j in range(0, len(temp_arr) - 1):
                maxpos = (my_balans // get_symbol_price(i)) // 10
                delta = temp_arr[j][0]
                contracts = temp_arr[j][1]
                if (symb_pr < (entr_pr + delta)):
                    close_position(symbol=i, s_l='SELL', quantity_l=
                    abs(round(maxpos * (contracts / 10), 3)))  # зарыть контракты из массива
                    new_balans = get_profit_balance()[1]
                    del proffit_array[0]
        if new_balans != 0:
            profit = new_balans - my_balans
            prt(str('Profit: ' + profit))
            prt(str('Balanse: ' + new_balans))
    except:
        pass


def opened_new_position():
    try:
        for i in new_position_long:
            if i not in opened_position_long:
                maxpos = (my_balans // get_symbol_price(i)) // 10
                open_position(symbol=i, s_l='long', quantity_l=maxpos)
                new_balans = get_profit_balance()[1]
                opened_position_long.append(i)
                new_position_long.remove(i)
                prt('Open Position : Long: ' + i + ' ' + maxpos)
                if new_balans != 0:
                    profit = new_balans - my_balans
                    prt(str('Profit: ' + profit))
                    prt(str('Balanse: ' + new_balans))
    except:
        prt('не открыл позицию')
    try:
        for i in new_position_short:
            if i not in opened_position_short:
                maxpos = (my_balans // get_symbol_price(i)) // 10
                open_position(symbol=i, s_l='short', quantity_l=maxpos)
                new_balans = get_profit_balance()[1]
                opened_position_short.append(i)
                new_position_short.remove(i)
                prt('Open Position : Short: ' + i + ' ' + maxpos)
                if new_balans != 0:
                    profit = new_balans - my_balans
                    prt(str('Profit: ' + profit))
                    prt(str('Balanse: ' + new_balans))
    except:
        pass


def prt(message):
    print(message)
    send_message(message)

print('Start')
send_message('Start')
first_data()
counter = 1
counter2 = 2
if __name__ == '__main__':
    while True:
        new_position_long = []
        new_position_short = []
        opened_position_long = []
        opened_position_short = []
        new_balans = 0
        my_balans = get_profit_balance()[1]
        print('================NEW_ROUND===============')
        for i in symbols:
            try:
                data = get_data(i)
                # print(data)
                if (data['RECOMMENDATION'] == 'STRONG_BUY' and (
                        data['SYMBOL'] not in longs)):  # если появляется в индикаторах новый сигнал,и его нет в старых
                    print(data['SYMBOL'], 'Buy')
                    text = data['SYMBOL'], 'Buy'
                    send_message(text)
                    longs.append(data['SYMBOL'])
                    new_position_long.append(data['SYMBOL'])
                    print(new_position_long)
                if (data['RECOMMENDATION'] == 'STRONG_SELL' and (
                        data['SYMBOL'] not in shorts)):  # если появляется в индикаторах новый сигнал,и его нет в старых
                    print(data['SYMBOL'], 'Sell')
                    text = data['SYMBOL'] + '   Sell'
                    send_message(text)
                    shorts.append(data['SYMBOL'])
                    new_position_short.append(data['SYMBOL'])
                    print(new_position_short)
                time.sleep(0.1)
                try:
                    opened_new_position()
                except:
                    prt('Не вышло открыть позицию...')

            except:
                prt('повторяю цикл.')

НАСТРОИТЬ ЦЕНУ ПОКУПКИ ДЛЯ МОНЕТ(КОЛИЧЕСТВО ПОКУПКИ ,ЧТОБЫ ПОКУПАТЬ ВЫШЕ МИНИМАЛКИ)