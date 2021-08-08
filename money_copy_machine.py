from coin_exchanger import *

<<<<<<< HEAD
with open('upbit.txt') as f:

    keys = f.readlines()
    access_key = keys[0][:-1]
    secret_key = keys[1]

jaebeom = pyupbit.Upbit(access_key, secret_key)
time.sleep(0.2)
majors, k = ['KRW-BTC', 'KRW-ETH', 'KRW-XRP', 'KRW-BCH', 'KRW-ETC', 'KRW-BTG'], 0.5

coins = select_coin(6, majors)  # 투자종목 선택하는데 25초 소요
target_price = get_target_price(coins, k)  # 목표가 계산하는데 1초 소요

now = datetime.datetime.now()
mid = datetime.datetime(now.year, now.month, now.day) + datetime.timedelta(days=1)
afternoon = datetime.datetime(now.year, now.month, now.day) + datetime.timedelta(hours=12)

send_alarm('오늘의 리포트입니다. 현재 원화 잔고 {0}KRW 입니다. 오늘 하루동안 매수를 시도할 코인은 {1}입니다.'.format(int(jaebeom.get_balance()), target_price))
time.sleep(0.5)  # json error

try:
    while True:
        now = datetime.datetime.now()

        if afternoon < now < afternoon + datetime.timedelta(seconds=10):
            send_alarm("좋은 오후입니다. 현재 coin exchanger 잘 돌아가고 있습니다. *^^*")

        if mid < now < mid + datetime.timedelta(seconds=10):
            try:
                account = jaebeom.get_balances()
                renew(jaebeom, account)

                coins = select_coin(6, majors)
                target_price = get_target_price(coins, k)

                mid = datetime.datetime(now.year, now.month, now.day) + datetime.timedelta(days=1)
                send_alarm('오늘의 리포트입니다. 현재 원화 잔고 {0}KRW 입니다. 오늘 하루동안 매수를 시도할 코인은 {1}입니다.'.format(int(jaebeom.get_balance()), coins))
                time.sleep(0.5)  # json error

            except TypeError:
                send_alarm('자정 프로세스 중 API를 너무 많이 호출했습니다 (JSONDecodeError). AWS 서버에 접속해 확인해주세요. coin exchanger를 종료합니다.')
                break

            except:
                send_alarm('자정 프로세스 중 원인 불명의 에러가 발생했습니다. AWS 서버에 접속해 확인해주세요. coin exchanger를 종료합니다.')
                break

        try:
            for coin in coins:

                current_price = pyupbit.get_current_price(coin)
                time.sleep(0.1)  # json 방지

                if current_price >= target_price[coin]:
                    amt = get_amount(coins)[coin]
                    krw = jaebeom.get_balance()
                    time.sleep(0.1)  # json error 방지
                    jaebeom.buy_market_order(coin, krw * amt)
                    time.sleep(0.1)  # json error 방지
                    send_alarm('{0}을 {1}KRW 만큼 구매했습니다.'.format(coin, krw * amt))

                    coins.remove(coin)

        except TypeError:
            try:
                for coin in coins:

                    current_price = pyupbit.get_current_price(coin)
                    time.sleep(0.3)  # json 방지

                    if current_price >= target_price[coin]:
                        amt = get_amount(coins)[coin]
                        krw = jaebeom.get_balance()
                        time.sleep(0.3)  # json error 방지
                        jaebeom.buy_market_order(coin, krw * amt)
                        time.sleep(0.3)  # json error 방지
                        send_alarm('{0}을 {1}KRW 만큼 구매했습니다.'.format(coin, krw * amt))

                        coins.remove(coin)
            except TypeError:
                send_alarm('자정 프로세스 중 API를 너무 많이 호출했습니다 (JSONDecodeError). AWS 서버에 접속해 확인해주세요. coin exchanger를 종료합니다.')
                break

        except:
            send_alarm("매매 프로세스 중 원인 불명의 에러가 발생했습니다. AWS 서버에 접속해 확인해주세요. coin exchanger를 종료합니다.")
            break

        time.sleep(1)

except KeyboardInterrupt:
    print('키보드 종료')
