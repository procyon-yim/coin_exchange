from coin_exchanger import *

with open('upbit.txt') as f:

    keys = f.readlines()
    access_key = keys[0][:-1]
    secret_key = keys[1]

jaebeom = pyupbit.Upbit(access_key, secret_key)
time.sleep(0.2)
majors = ['KRW-BTC', 'KRW-ETH', 'KRW-XRP', 'KRW-BCH', 'KRW-ETC', 'KRW-BTG']
k = 0.5

coins = select_coin(6, majors)  # 투자종목 선택하는데 25초 소요
target_price = get_target_price(coins, k)  # 목표가 계산하는데 1초 소요
start_balance  = jaebeom.get_balance()

now = datetime.datetime.now()
mid = datetime.datetime(now.year, now.month, now.day) + datetime.timedelta(days=1)

send_alarm('오늘의 리포트입니다. 현재 원화 잔고 {0}KRW 입니다. 오늘 하루동안 매수를 시도할 코인은 {1}입니다. 현재 서버 시각 {2}'.format(int(start_balance), target_price, now))
time.sleep(0.5)  # json error

try:
    while True:
        now = datetime.datetime.now()

        if mid < now < mid + datetime.timedelta(seconds=10):
            try:
                account = jaebeom.get_balances()
                renew(jaebeom, account)

                coins = select_coin(6, majors)
                target_price = get_target_price(coins, k)
                start_balance = jaebeom.get_balance()
                mid = datetime.datetime(now.year, now.month, now.day) + datetime.timedelta(days=1)
                send_alarm('오늘의 리포트입니다. 현재 원화 잔고 {0}KRW 입니다. 오늘 하루동안 매수를 시도할 코인은 {1}입니다. 현재 서버시각 {2}'.format(int(start_balance), target_price, now))
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
                    time.sleep(0.1)  # json error 방지
                    jaebeom.buy_market_order(coin, start_balance * amt)
                    time.sleep(0.1)  # json error 방지
                    send_alarm('{0}을 {1}KRW 만큼 구매했습니다.'.format(coin, start_balance * amt))

                    coins.remove(coin)

        except TypeError:
            try:
                for coin in coins:

                    current_price = pyupbit.get_current_price(coin)
                    time.sleep(0.3)  # json 방지

                    if current_price >= target_price[coin]:
                        amt = get_amount(coins)[coin]
                        time.sleep(0.3)  # json error 방지
                        jaebeom.buy_market_order(coin, start_balance * amt)
                        time.sleep(0.3)  # json error 방지
                        send_alarm('{0}을 {1}KRW 만큼 구매했습니다.'.format(coin, start_balance * amt))

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
