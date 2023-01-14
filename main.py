import time
import requests
from tradingview_ta import TA_Handler, Interval, Exchange
from binance.client import Client
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import copy

INTERVAL = Interval.INTERVAL_5_MINUTES  # желательно 4ч - или дневные для этой стратегии

TOKEN = '5886578012:AAHIPhYEMgf_UxqbLDR0v5NJc7XjY-0X5AI'
CHAT = '624736798'

KEY = '6ba95e7ed67fff7357a6a9fdca47e350852a2d62668d1db9570e5ae9db99e9c3'
SECRET = '793aebcbcff748c0350cd24979964541e28cbe8491e2005853c52bec0cd4473f'

client = Client(KEY, SECRET, tld='https://testnet.binancefuture.com', testnet=True)
# stop_percent = 0.004
eth_proffit_array = [[2.2, 4], [3.5, 3.5], [5.5, 1.5], [7, 1], [80, 2], [150, 1], [200, 1], [200, 0]]
proffit_array = copy.copy(eth_proffit_array)
# парирумчик

def get_futures_klines(symbol, limit=50):
    x = requests.get('https://binance.com/fapi/v1/klines?symbol=' + symbol + '&limit=' + str(
        limit) + '&interval=1h')  # ===================СВЕЧА=======================
    df = pd.DataFrame(x.json())
    df.columns = ['open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'd1', 'd2', 'd3', 'd4', 'd5']
    df = df.drop(['d1', 'd2', 'd3', 'd4', 'd5'], axis=1)
    df['open'] = df['open'].astype(float)
    df['high'] = df['high'].astype(float)
    df['low'] = df['low'].astype(float)
    df['close'] = df['close'].astype(float)
    df['volume'] = df['volume'].astype(float)
    return (df)

def get_opened_positions(symbol):
    status = client.futures_account()
    positions = pd.DataFrame(status['positions'])
    a = positions[positions['symbol'] == symbol]['positionAmt'].astype(float).tolist()[0]
    leverage = int(positions[positions['symbol'] == symbol]['leverage'])
    entryprice = positions[positions['symbol'] == symbol]['entryPrice']
    profit = float(status['totalUnrealizedProfit'])
    balance = round(float(status['totalWalletBalance']), 2)
    if a > 0:
        pos = "long"
    elif a < 0:
        pos = "short"
    else:
        pos = ""
    return ([pos, a, profit, leverage, balance, round(float(entryprice), 3), 0])

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

telegram_delay=12
def getTPSLfrom_telegram():
    strr = 'https://api.telegram.org/bot' + TOKEN + '/getUpdates'
    response = requests.get(strr)
    rs = response.json()
    if (len(rs['result']) > 0):
        rs2 = rs['result'][-1]
        rs3 = rs2['message']
        textt = rs3['text']
        datet = rs3['date']

        if (time.time() - datet) < telegram_delay:
            if (len(rs['result']) > 0):
                rs2 = rs['result'][-1]
                rs3 = rs2['message']
                textt = rs3['text']
                datet = rs3['date']
                for i in opened_position_long:
                    if i.lower() in textt:
                        send_message('рисую...')
                        graphik(i.upper())
                        price = get_symbol_price(i.upper())  # float(data['kline']['close_price'])
                        procent = round(((get_opened_positions(i)[5] / price) * 100) - 100, 2)
                        send_message(procent+'%')
                for i in opened_position_short:
                    if i.lower() in textt:
                        send_message('рисую...')
                        graphik(i.upper())
                        price = get_symbol_price(i.upper())  # float(data['kline']['close_price'])
                        procent = round(((get_opened_positions(i)[5] / price) * 100) - 100, 2)
                        send_message(procent + '%')
                if 'pars' in textt:
                    l=opened_position_long
                    h=opened_position_short
                    send_message(f'Long: {l}\n Short: {h}')
                if 'help' in textt:
                    send_message('напиши пару - получишь график ,  quit - отключить бота   balans - баланс   hello - проверить бота   close _ pos - закрыть позиции  price - прайс символа')
                if 'quit' in textt:
                    send_message('Выключаюсь...')
                    quit()
                if 'exit' in textt:
                    exit()
                if 'balance' in textt:
                    status = client.futures_account()
                    balance = round(float(status['totalWalletBalance']), 2)
                    send_message(balance+'$')
                if 'hello' in textt:
                    send_message('Всё ок,работаем')
                # if 'close_pos' in textt:
                #     position = get_opened_positions(symbol)
                #     open_sl = position[0]
                #     quantity = position[1]
                #     #  print(open_sl,quantity)
                #     close_position(symbol, open_sl, abs(quantity))
                #     telegram_bot_sendtext('Позиция закрыта')

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
            try:
                if (data['RECOMMENDATION'] == 'STRONG_BUY'):  # перебираем их
                    longs.append(data['SYMBOL'])
                    # print(data['SYMBOL'], 'Buy')
            except:
                pass
            try:
                if (data['RECOMMENDATION'] == 'STRONT_SELL'):
                    shorts.append(data['SYMBOL'])
                    # print(data['SYMBOL'], 'Short')
            except:
                pass
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
            "price": close_price,
            "leverage": "10"

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
            "price": close_price,
            "leverage": "10"
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
            "price": close_price,
            "leverage": "10"

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
            "price": close_price,
            "leverage": "10"
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
    return ([profit, balance])


def get_quanty_position(symbol):  # обьём монет в позиции
    status = client.futures_account()
    positions = pd.DataFrame(status['positions'])
    a = positions[positions['symbol'] == symbol]['positionAmt'].astype(float).tolist()[0]
    return a


def entry_price(symbol):  # цена входа в позицию
    status = client.futures_account()
    positions = pd.DataFrame(status['positions'])
    entryprice = positions[positions['symbol'] == symbol]['entryPrice']
    return round(float(entryprice), 3)


# def profit_stoploss():
#     try:
#         for i in opened_position_long:
#             temp_arr = copy.copy(proffit_array)
#             symb_pr = get_symbol_price(i)
#             stop_loss = entry_price(i) * (1 - stop_percent)
#             entr_pr = entry_price(i)
#             if symb_pr<stop_loss:
#                 close_position(symbol=i,s_l='long')

def profit_and_stop_loss():
    for i in opened_position_long:
        print('перебор long')
        QTY = get_opened_positions(i)[1]
        #temp_arr = copy.copy(proffit_array)
        # usd = 12
        symb_pr = get_symbol_price(i)
        stop_loss = entry_price(i) /1.001 #нижняя граница умножай на плечё
        stop_profit = entry_price(i) * 1.0006 #верхняя граница умножай на плечё
        print('STOPLOSS'+stop_loss)
        print('STOP_PROFIT'+stop_profit)
        #entr_pr = entry_price(i)
        # maxpos = symb_pr/usd
        if symb_pr <= stop_loss:
            prt('Пробую закрыть ордер')
            close_position(symbol=i, s_l='long', quantity_l=abs(QTY))
            opened_position_long.remove(i)
            prt('===STOP_LOSS===')
        if symb_pr >= stop_profit:
            prt('Пробую закрыть ордер')
            close_position(symbol=i, s_l='long', quantity_l=abs(QTY))
            opened_position_long.remove(i)
            prt('====Take_Profit===')
        # for j in range(0, len(temp_arr) - 1):
        #     maxpos = (my_balans // get_symbol_price(i)) // 10
        #     delta = temp_arr[j][0]
        #     contracts = temp_arr[j][1]
        #     if symb_pr > (entr_pr + delta):
        #         close_position(symbol=i, s_l='long', quantity_l=
        #         abs(round(maxpos * (contracts / 10), 3)))  # зарыть контракты из массива
        #         new_balans = get_profit_balance()[1]
        #         del proffit_array[0]
    for g in opened_position_short:
        print('перебор short')
        #temp_arr = copy.copy(proffit_array)
        #usd=12
        symb_pr = get_symbol_price(g)
        stop_loss2 = entry_price(g) * 1.001
        stop_profit2 = entry_price(g) /1.0006
        print('STOPLOSS' + stop_loss2)
        print('STOP_PROFIT' + stop_profit2)
        #maxpos = symb_pr/usd
        QTY2 = get_opened_positions(g)[1]
        if symb_pr >= stop_loss2:
            prt('Пробую закрыть ордер')
            close_position(symbol=g, s_l='short', quantity_l=abs(QTY2))
            opened_position_short.remove(g)
            prt('===STOP_LOSS===')
        if symb_pr <= stop_profit2:
            prt('Пробую закрыть ордер')
            close_position(symbol=g, s_l='short', quantity_l=abs(QTY2))
            opened_position_short.remove(g)
            prt('===Take_Profit===')
        # for j in range(0, len(temp_arr) - 1):
        #     maxpos = (my_balans // get_symbol_price(i)) // 10
        #     delta = temp_arr[j][0]
        #     contracts = temp_arr[j][1]
        #     if (symb_pr < (entr_pr + delta)):
        #         close_position(symbol=i, s_l='short', quantity_l=
        #         abs(round(maxpos * (contracts / 10), 3)))  # зарыть контракты из массива
        #         new_balans = get_profit_balance()[1]
        #         del proffit_array[0]


def opened_new_position():
    my_balans = get_profit_balance()[1]
    try:
        for i in new_position_long:
            if i not in opened_position_long:
                # pr = get_symbol_price(i)
                # usd = 20
                # maxpos = usd / pr
                maxpos = round((my_balans / get_symbol_price(i)),1)
                new_position_long.remove(i)
                open_position(symbol=i, s_l='long', quantity_l=maxpos)
                opened_position_long.append(i)
                prt('Open Position : Long: ' + i + ' ' + str(maxpos))
                prt(get_symbol_price(i))
                prt(f'Long: {opened_position_long}\nShort: {opened_position_short}')
                #graphik(i)
    except:
        pass
    try:
        for i in new_position_short:
            if i not in opened_position_short:
                # pr = get_symbol_price(i)
                # usd = 20
                # maxpos = usd / pr
                maxpos = round((my_balans / get_symbol_price(i)),1)
                new_position_short.remove(i)
                open_position(symbol=i, s_l='short', quantity_l=maxpos)
                opened_position_short.append(i)
                prt('Open Position : Short: ' + i + ' ' + str(maxpos))
                prt(get_symbol_price(i))
                prt(f'Long: {opened_position_long}\nShort: {opened_position_short}')
                #graphik(i)
    except:
        pass
# ikb=InlineKeyboardMarkup(row_width=3)
# ib1=InlineKeyboardButton(text='1',
#                                  callback_data=1)
#
#
# @dp.message_handler(commands=['pars'])
# async def startcom(message: types.Message):
#     await bot.send_message(chat_id=message.from_user.id,
#                           text='Пары: ',
#                           reply_markup=ikb)

def prt(message):
    print(message)
    send_message('I-bot: '+str(message))


def graphik(symbol):
    df = get_futures_klines(symbol=symbol, limit=50)
    up = df[df.close >= df.open]
    down = df[df.close < df.open]

    width = .4  # .4 стандарт.-ширина свечей
    width2 = .05  # .05 -вторая ширина

    col1 = 'green'
    col2 = 'red'
    fig, ax = plt.subplots(facecolor='grey', edgecolor='black')
    ax.set_facecolor('black')
    ax.set_xlim(0, 55)
    # время
    a = time.ctime()
    a = a.split()
    times = a[3][0:5]
    # график пунктиром
    plt.plot(df.index, df.close, color='white', alpha=0.6, linestyle='-.')
    # свечи вверх
    plt.bar(up.index, up.close - up.open, width, bottom=up.open, color=col1)
    plt.bar(up.index, up.high - up.close, width2, bottom=up.close, color=col1)
    plt.bar(up.index, up.low - up.open, width2, bottom=up.open, color=col1)
    # свечи вниз
    plt.bar(down.index, down.close - down.open, width, bottom=down.open, color=col2)
    plt.bar(down.index, down.high - down.open, width2, bottom=down.open, color=col2)
    plt.bar(down.index, down.low - down.close, width2, bottom=down.close, color=col2)
    plt.grid(color='turquoise', linewidth=0.2, linestyle='--')
    prices = client.futures_mark_price()
    df = pd.DataFrame(prices)
    price = float(df[df['symbol'] == symbol]['markPrice'])

    ax.set_title(f'{symbol}   {times}', fontsize=20, color='blue')
    # линия цены
    x = [0, 55]
    y = [price, price]
    plt.plot(x, y, label=f'Pr {round(price, 4)}', color='white', linestyle='--', marker='', linewidth=0.5)
    # линии стоп лосса
    entryprice = get_opened_positions(symbol)[5]
    pos = get_opened_positions(symbol)[0]
    if pos == 'long':
        stoploss = entryprice / 1.004
        x1 = [0, 55]
        y1 = [stoploss, stoploss]
        plt.plot(x1, y1, label=f'st {round(stoploss, 4)} -0.4%', color='red', linestyle='--', marker='',
                 linewidth=1)
        x2 = [0, 55]
        y2 = [entryprice, entryprice]
        plt.plot(x2, y2, label=f'long {round(entryprice, 4)}', color='green', linestyle='--', marker='', linewidth=1.5)
        p1 = entryprice * 1.005
        xx1 = [0, 55]
        yy1 = [p1, p1]
        plt.plot(xx1, yy1, label=f'p {round(p1, 4)} 0.5%', color='#74F827', linestyle='--', marker='', alpha=0.8,
                 linewidth=0.8)
    if pos == 'short':
        stoploss2 = entryprice * 1.004
        x11 = [0, 55]
        y11 = [stoploss2, stoploss2]
        plt.plot(x11, y11, label=f'st {round(stoploss2, 4)} -0.4%', color='red', linestyle='--', marker='',
                 linewidth=1)
        x22 = [0, 55]
        y22 = [entryprice, entryprice]
        plt.plot(x22, y22, label=f'short {round(entryprice, 4)}', color='#F80063', linestyle='--', marker='',
                 linewidth=1.5)
        p11 = entryprice / 1.005
        xx11 = [0, 55]
        yy11 = [p11, p11]
        plt.plot(xx11, yy11, label=f'p1 {round(p11, 4)} 0.5%', color='#F84E4E', linestyle='--', marker='',
                 alpha=0.8, linewidth=0.8)

    # наклон галочек
    plt.xticks(np.arange(0, 55, 5), rotation=15, ha='right')
    plt.legend(loc='best')

    fig.savefig(f'C:/Users/Admin/Desktop/indic./graph')

    # отправка фото
    url = 'https://api.telegram.org/bot' + TOKEN + '/sendPhoto';
    files = {'photo': open(r"C:\Users\Admin\Desktop\indic\graph.png", 'rb')}
    data = {'chat_id': "624736798"}
    r = requests.post(url, files=files, data=data)
    return r.json()




print('Start')
send_message('Start')
#first_data()
counter = 1
counter2 = 2
if __name__ == '__main__':
    new_position_long = []
    new_position_short = []
    opened_position_long = []
    opened_position_short = []
    send_message('Начинаю...')
    while True:
        new_balans = 0
        my_balans = get_profit_balance()[1]
        print('================NEW_ROUND===============')
        for i in symbols:
            try:
                getTPSLfrom_telegram()
            except:
                pass
            try:
                data = get_data(i)
                # print(data)
                if (data['RECOMMENDATION'] == 'STRONG_BUY' and (
                        data['SYMBOL'] not in longs)):  # если появляется в индикаторах новый сигнал,и его нет в старых
                    print(data['SYMBOL'], 'Buy')
                    # text = data['SYMBOL'], 'Buy'
                    # send_message(text)
                    longs.append(data['SYMBOL'])
                    new_position_long.append(data['SYMBOL'])
                    print(new_position_long)
                    # try:
                    #     opened_new_position()
                    #     prt('Позиция LONG открыта '+ i)
                    # except:
                    #     print('No Pos Buy')
                if (data['RECOMMENDATION'] == 'STRONG_SELL' and (
                        data['SYMBOL'] not in shorts)):  # если появляется в индикаторах новый сигнал,и его нет в старых
                    print(data['SYMBOL'], 'Sell')
                    # text = data['SYMBOL'] + '   Sell'
                    # send_message(text)
                    shorts.append(data['SYMBOL'])
                    new_position_short.append(data['SYMBOL'])
                    print(new_position_short)
                opened_new_position()
                for i in opened_position_long:
                    print('перебор long')
                    #print(i)
                    QTY = get_quanty_position(i)
                    #print('1')
                    symb_pr = get_symbol_price(i)
                    #print('2')
                    stop_loss = round(entry_price(i) / 1.001,3)  # нижняя граница умножай на плечё
                    #print('3')
                    stop_profit = round(entry_price(i) * 1.0006,3)  # верхняя граница умножай на плечё
                    #print('4')
                    # print('STOPLOSS' + stop_loss)
                    # print('STOP_PROFIT' + stop_profit)
                    # entr_pr = entry_price(i)
                    # maxpos = symb_pr/usd
                    try:
                        if symb_pr <= stop_loss:
                            prt('Пробую закрыть ордер')
                            close_position(symbol=i, s_l='long', quantity_l=abs(QTY))
                            opened_position_long.remove(i)
                            prt('===STOP_LOSS==='+'--'+i)
                    except:
                        pass
                    try:
                        if symb_pr >= stop_profit:
                            prt('Пробую закрыть ордер2')
                            close_position(symbol=i, s_l='long', quantity_l=abs(QTY))
                            opened_position_long.remove(i)
                            prt('====Take_Profit==='+'--'+i)
                    except:
                        pass
                    # for j in range(0, len(temp_arr) - 1):
                    #     maxpos = (my_balans // get_symbol_price(i)) // 10
                    #     delta = temp_arr[j][0]
                    #     contracts = temp_arr[j][1]
                    #     if symb_pr > (entr_pr + delta):
                    #         close_position(symbol=i, s_l='long', quantity_l=
                    #         abs(round(maxpos * (contracts / 10), 3)))  # зарыть контракты из массива
                    #         new_balans = get_profit_balance()[1]
                    #         del proffit_array[0]
                for g in opened_position_short:
                    print('перебор short')
                    QTY2 = get_quanty_position(g)
                    # temp_arr = copy.copy(proffit_array)
                    # usd=12
                    symb_pr = get_symbol_price(g)
                    stop_loss2 = round(entry_price(g) * 1.001,3)
                    stop_profit2 = round(entry_price(g) / 1.0006,3)
                    # print('STOPLOSS' + stop_loss2)
                    # print('STOP_PROFIT' + stop_profit2)
                    # maxpos = symb_pr/usd
                    try:
                        if symb_pr >= stop_loss2:
                            prt('Пробую закрыть ордер')
                            close_position(symbol=g, s_l='short', quantity_l=abs(QTY2))
                            opened_position_short.remove(g)
                            prt('===STOP_LOSS==='+'--'+g)
                    except:
                        pass
                    try:
                        if symb_pr <= stop_profit2:
                            prt('Пробую закрыть ордер2')
                            close_position(symbol=g, s_l='short', quantity_l=abs(QTY2))
                            opened_position_short.remove(g)
                            prt('===Take_Profit==='+'--'+g)
                    except:
                        pass
                    # for j in range(0, len(temp_arr) - 1):
                    #     maxpos = (my_balans // get_symbol_price(i)) // 10
                    #     delta = temp_arr[j][0]
                    #     contracts = temp_arr[j][1]
                    #     if (symb_pr < (entr_pr + delta)):
                    #         close_position(symbol=i, s_l='short', quantity_l=
                    #         abs(round(maxpos * (contracts / 10), 3)))  # зарыть контракты из массива
                    #         new_balans = get_profit_balance()[1]
                    #         del proffit_array[0]
            except:
                print('повторяю цикл.')