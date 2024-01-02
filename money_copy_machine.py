from coin_exchanger import *

username = "Xaveynt6kyfrx3Ojtxj0KoSdpHcgn93TBe795kY1"
password = "0aS1edeSChokCMQbUkzs3xOURz5g731ipvopNt1c"
user = pyupbit.Upbit(username, password)

coins = ['KRW-BTC', 'KRW-ETH', 'KRW-XRP', 'KRW-ADA', 'KRW-DOGE']  # list of coins to exchange
k = 0.5
# breakout coefficient (see https://www.whselfinvest.com/en-lu/trading-platform/free-trading-strategies/tradingsystem/56-volatility-break-out-larry-williams-free)
amount = get_amount(coins)
target_price = get_target_price(coins, k)
start_balance  = user.get_balance()
now = datetime.datetime.now()
mid = datetime.datetime(now.year, now.month, now.day) + datetime.timedelta(days=1)
notification = 'Current time is {2}, Current Balance is {0}KRW. Today\'s targets are {1}.'.format(int(start_balance), amount, now)
send_alarm(notification)

try:
    while True:
        now = datetime.datetime.now()

        if mid < now < mid + datetime.timedelta(seconds=10):
            try:
                renew(user, user.get_balances())
                coins = ['KRW-BTC', 'KRW-ETH', 'KRW-XRP', 'KRW-ADA', 'KRW-DOGE']
                k = 0.5
                amount = get_amount(coins)
                target_price = get_target_price(coins, k)
                start_balance = user.get_balance()
                now = datetime.datetime.now()
                mid = datetime.datetime(now.year, now.month, now.day) + datetime.timedelta(days=1)
                notification = 'Current time is {2}, Current Balance is {0}KRW. Today\'s targets are {1}.'.format(int(start_balance), amount, now)
                send_alarm(notification)
            except TypeError:
                notification = "An unexpected error occured. Terminating program. Please reboot via the mobile AWS application"
                send_alarm(notification)
                break

            except Exception as e:
                notification = "An unexpected error occured. Terminating program. Please reboot via the mobile AWS application"
                send_alarm(notification)
                break

        try:
            for coin in coins:
                current_price = pyupbit.get_current_price(coin)
                time.sleep(0.1)  # This is because you can call an Upbit API only 10 times a second

                if current_price >= target_price[coin]:
                    qtty = amount[coin]
                    time.sleep(0.1)

                    if qtty == 0:
                        coins.remove(coin)

                    else:
                        user.buy_market_order(coin, start_balance * qtty)
                        time.sleep(0.1)
                        coins.remove(coin)

        except:
            try:
                for coin in coins:
                    current_price = pyupbit.get_current_price(coin)
                    time.sleep(0.5)

                    if current_price >= target_price[coin]:
                        qtty = amount[coin]
                        time.sleep(0.5)
                        if qtty == 0:
                            coins.remove(coin)
                        else:
                            user.buy_market_order(coin, start_balance * qtty)
                            time.sleep(0.5)
                            coins.remove(coin)

            except Exception as e:
                notification = "An unexpected error occured. Terminating program. Please reboot via the mobile AWS application"
                send_alarm(notification)
                break

        time.sleep(1)

except KeyboardInterrupt:
    print('keyboard interruption')
