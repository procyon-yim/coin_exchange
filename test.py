from coin_exchanger import *

user, pwd = login('upbit.txt')
jaebeom = pyupbit.Upbit(user, pwd)

df = pyupbit.get_ohlcv('KRW-BTC', interval='minute60', to=datetime.datetime.now())
yday = df.iloc[-25]  # 어제 00:00
delta = abs(max(df.iloc[-25:]['high']) - min(df.iloc[-25:]['low'])) / yday['close']

print(yday)
print(delta)