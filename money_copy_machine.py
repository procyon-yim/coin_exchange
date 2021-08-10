from coin_exchanger import *

with open('upbit.txt') as f:
    keys = f.readlines()
    access_key = keys[0][:-1]
    secret_key = keys[1]

jaebeom = pyupbit.Upbit(access_key, secret_key)
# 주문 외 Exchange API는 초당 30회 호출 가능. (https://github.com/sharebook-kr/pyupbit 참고)
majors = ['KRW-BTC', 'KRW-ETH', 'KRW-XRP', 'KRW-BCH', 'KRW-ETC', 'KRW-BTG']
k = 0.5
coins = select_coin(6, majors)  # 투자종목 선택하는데 25초 소요
target_price = get_target_price(coins, k)  # 목표가 계산하는데 1초 소요
start_balance  = jaebeom.get_balance()  # 이 돈을 가지고 시작하는거다.
now = datetime.datetime.now()
mid = datetime.datetime(now.year, now.month, now.day) + datetime.timedelta(days=1)
send_alarm('mail.txt', '현재 시각 {2}, 현재 잔고 {0}KRW. 매수를 시도할 코인은 {1}.'.format(int(start_balance), target_price, now))

try:
    while True:
        now = datetime.datetime.now()

        if mid < now < mid + datetime.timedelta(seconds=10):
            try:
                renew(jaebeom, jaebeom.get_balances())
                coins = select_coin(6, majors)
                target_price = get_target_price(coins, k)
                start_balance = jaebeom.get_balance()
                mid = datetime.datetime(now.year, now.month, now.day) + datetime.timedelta(days=1)
                send_alarm('mail.txt', '현재 시각 {2}, 현재 잔고 {0}KRW. 매수를 시도할 코인은 {1}.'.format(int(start_balance), target_price, now))

            except TypeError:
                send_alarm('mail.txt', '자정 프로세스 중 API를 너무 많이 호출했습니다 (JSONDecodeError). AWS 서버에 접속해 확인해주세요. MCM을 종료합니다.')
                break

            except Exception as e:
                send_alarm('mail.txt', '자정 프로세스 중 에러 발생. {} MCM을 종료합니다.'.format(e))
                break

        try:
            for coin in coins:
                current_price = pyupbit.get_current_price(coin)
                time.sleep(0.1)  # (quotation api는 초당 10회 가능)

                if current_price >= target_price[coin]:
                    amt = get_amount(coins)[coin]
                    time.sleep(0.1)  # json error 방지
                    jaebeom.buy_market_order(coin, start_balance * amt)
                    time.sleep(0.1)  # json error 방지
                    send_alarm('mail.txt', '{0}을 {1}KRW 만큼 구매했습니다.'.format(coin, start_balance * amt))
                    coins.remove(coin)

        except Exception as e:
            send_alarm('mail.txt', "매매 프로세스 중 에러 발생. {}. MCM을 종료합니다.".format(e))
            break

        time.sleep(1)

except KeyboardInterrupt:
    print('키보드 종료')
