import time
import pyupbit
import datetime
import pandas as pd
import telegram

TOKEN = '1919980133:AAG845Pwz1i4WCJvaaamRT-_QE0uezlvA9A'
ID = '1796318367'
bot = telegram.Bot(TOKEN)


def get_start_time(ticker):
    """시작 시간 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start_time = df.index[0]
    return start_time

def get_current_price(ticker):
    """현재가 조회"""
    return pyupbit.get_orderbook(tickers=ticker)[0]["orderbook_units"][0]["ask_price"]

def get_volatility(ticker):
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    df['volatility'] = (df['close']/df['open']-1)*100
    volatility = df.iloc[-1]['volatility']
    return volatility

def get_minute(ticker):
    df = pyupbit.get_ohlcv(ticker, interval="minute1", count=2)
    df['volatility'] = (df['close']/df['open']-1)*100
    volatility = df.iloc[-1]['volatility']
    return volatility

def check_vol(ticker):
    df_d = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    df_m = pyupbit.get_ohlcv(ticker, interval="minute1", count=2)
    pre=(df_m.iloc[0]['close']/df_d['open']-1)*100
    post=(df_m.iloc[-1]['close']/df_d['open']-1)*100
    result=[pre.values,post.values]
    return result

def get_top5(rq):
    tickers = pyupbit.get_tickers(fiat="KRW")
    dfs = []
    for i in range(len(tickers)):
        volatility = round(get_volatility(tickers[i]),2)
        dfs.append(volatility)
        time.sleep(0.06)

    volatility = pd.DataFrame({"volatility": dfs})
    ticker = pd.DataFrame({"ticker": pyupbit.get_tickers(fiat="KRW")})
    sum = [ticker, volatility]
    all_volatility = pd.concat(sum, axis =1)
    final=all_volatility.sort_values(by = "volatility", ascending=False)
    if rq == 0:
        #Dataframe을 list로 변환
        #result = final.iloc[:5]
        result = final.iloc[0].values.tolist()
    elif rq ==1:
        #상위 상승률 top5 ticker명만 뽑기
        result1 = final.iloc[:5]['ticker'].values.tolist()
    else:
        #상위 상승률 top5 상승률만 뽑기
        result2 = final.iloc[:5]['volatility'].values.tolist()
    return result[0]

bot.sendMessage(ID, "start")
#check_vol('KRW-FLOW')
pre_check = False
print('되나'+str(pre_check))
while True:
    try:
        now = datetime.datetime.now()
        start_time = get_start_time("KRW-ETH")
        end_time = start_time + datetime.timedelta(days=1)
        if start_time < now < end_time - datetime.timedelta(seconds=5):
            if pre_check == False:
                pre_check_time = datetime.datetime.now()
                pre_ticker = get_top5(0)
                pre_check = True
                print('변경 전 pre_ticker check'+str(pre_ticker))
            post_check_time = datetime.datetime.now()
            post_ticker = get_top5(0)
            post_check_endtime = datetime.datetime.now()
            print('변수 비교 전'+str(post_ticker))
            if pre_ticker == post_ticker:
                pre_ticker = post_ticker
                print('같음 확인...'+str(pre_ticker)+','+str(post_ticker))
            else:
                current_price = get_current_price(post_ticker)
                check = check_vol(post_ticker)
                print('바뀌기 전...'+str(pre_ticker))
                if check[1]>check[0]:
                    bot.sendMessage(ID, str(pre_check_time.strftime('%d/%b, %H:%M:%S')) + '\n'
                                        + "pre_ticker:" + str(pre_ticker) + '\n'
                                        + str(post_check_time.strftime('%d/%b, %H:%M:%S')) + '\n'
                                        + "post_ticker:" + str(post_ticker) + '\n'
                                        + str(post_check_endtime.strftime('%d/%b, %H:%M:%S')))
                    current_time = datetime.datetime.now()
                    bot.sendMessage(ID, str(current_time.strftime('%d/%b, %H:%M:%S')) + '\n'
                                    + str(post_ticker) + '\n'
                                    + "pre_vol:" + str(check[0]) + "%" '\n'
                                    + "post_vol:" + str(check[1]) + "%" '\n')
                    print('바뀐 후')
                    print(post_ticker)
                    pre_ticker = post_ticker
                    print('변수 변경 중....')
                    print(pre_ticker)
                    print('pre_ticker 변경 확인 완료')
        else:
            bot.sendMessage(ID, 'rest...')
        time.sleep(1)
    except Exception as e:
        print(e)
        bot.sendMessage(ID, e)
        time.sleep(1)
