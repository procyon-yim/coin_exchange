from coin_exchanger import *

username, password = login('upbit.txt')
jaebeom = pyupbit.Upbit(username, password)

renew(jaebeom, jaebeom.get_balances())
