import pyupbit
from coin_exchanger import login

username, password = login('upbit.txt')
user = pyupbit.Upbit(username, password)

print(user.get_balances())