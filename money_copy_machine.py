from coin_exchanger import *

username, password = login('upbit.txt')
jaebeom = pyupbit.Upbit(username, password)

# 주문 외 Exchange API는 초당 30회 호출 가능. (https://github.com/sharebook-kr/pyupbit 참고)

coins = ['KRW-BTC', 'KRW-ETH', 'KRW-XRP', 'KRW-ADA', 'KRW-DOGE']
k = 0.5
amount = get_amount(coins)
target_price = get_target_price(coins, k)  # 목표가 계산하는데 1초 소요
start_balance  = jaebeom.get_balance()  # 이 돈을 가지고 시작하는거다.
now = datetime.datetime.now()
mid = datetime.datetime(now.year, now.month, now.day) + datetime.timedelta(days=1)
send_alarm('mail.txt', '현재 시각 {2}, 현재 잔고 {0}KRW. 매수 비중은 {1}.'.format(int(start_balance), amount, now))

try:
    while True:
        now = datetime.datetime.now()

        if mid < now < mid + datetime.timedelta(seconds=10):
            try:
                renew(jaebeom, jaebeom.get_balances())

                coins = ['KRW-BTC', 'KRW-ETH', 'KRW-XRP', 'KRW-ADA', 'KRW-DOGE']
                k = 0.5
                amount = get_amount(coins)
                target_price = get_target_price(coins, k)
                start_balance = jaebeom.get_balance()
                now = datetime.datetime.now()
                mid = datetime.datetime(now.year, now.month, now.day) + datetime.timedelta(days=1)
                send_alarm('mail.txt', '현재 시각 {2}, 현재 잔고 {0}KRW. 매수 비중은 {1}.'.format(int(start_balance), amount, now))

            except TypeError:
                send_alarm('mail.txt', '자정 프로세스 중 API를 너무 많이 호출했습니다 (JSONDecodeError). MCM을 종료합니다.')
                break

            except Exception as e:
                send_alarm('mail.txt', '자정 프로세스 중 에러 발생. {} MCM을 종료합니다.'.format(e))
                break

        try:
            for coin in coins:
                current_price = pyupbit.get_current_price(coin)
                time.sleep(0.1)  # (quotation api는 초당 10회 가능)

                if current_price >= target_price[coin]:
                    qtty = amount[coin]
                    time.sleep(0.1)  # json error 방지

                    if qtty == 0:
                        coins.remove(coin)

                    else:
                        jaebeom.buy_market_order(coin, start_balance * qtty)
                        time.sleep(0.1)  # json error 방지
                        coins.remove(coin)

        except:
            try:
                for coin in coins:
                    current_price = pyupbit.get_current_price(coin)
                    time.sleep(0.5)  # (quotation api는 초당 10회 가능)

                    if current_price >= target_price[coin]:
                        qtty = amount[coin]
                        time.sleep(0.5)  # json error 방지
                        if qtty == 0:
                            coins.remove(coin)
                        else:
                            jaebeom.buy_market_order(coin, start_balance * qtty)
                            time.sleep(0.5)  # json error 방지
                            coins.remove(coin)

            except Exception as e:
                send_alarm('mail.txt', "매매 프로세스 중 에러 발생. {}. MCM을 종료합니다.".format(e))
                break

        time.sleep(1)

except KeyboardInterrupt:
    print('keyboard interruption')
