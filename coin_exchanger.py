import pyupbit
import time
import datetime
import smtplib
from email.mime.text import MIMEText
import random


def send_alarm(text):
    sendEmail = "max5972@naver.com"
    recvEmail = "jaebeom.yim@seh.ox.ac.uk"
    with open('mail.txt') as f:
        password = f.readline()

    smtpName = "smtp.naver.com"  # smtp 서버 주소
    smtpPort = 587  # smtp 포트 번호

    msg = MIMEText(text)  # MIMEText(text , _charset = "utf8")

    msg['Subject'] = "Coin Exchanger's Report"
    msg['From'] = sendEmail
    msg['To'] = recvEmail

    s = smtplib.SMTP(smtpName, smtpPort)  # 메일 서버 연결
    s.starttls()  # TLS 보안 처리
    s.login(sendEmail, password)  # 로그인
    s.sendmail(sendEmail, recvEmail, msg.as_string())  # 메일 전송, 문자열로 변환하여 보냅니다.
    s.close()  # smtp 서버 연결을 종료합니다.
    time.sleep(1)  # json 오류 때문에.


def get_target_price(tickers, k_value):
    '''
    <변동성 돌파 전략>을 바탕으로 해당 일의 매수가를 구해주는 메소드
    :param ticker: (str) 코인의 티커
    :param k_value: (float) k값. 주로 0.5 보수적일수록 높게, 도전적일수록 낮게
    :return: (float) 당일 매입가
    '''

    target = dict()

    for ticker in tickers:

        df = pyupbit.get_ohlcv(ticker, interval='minute60', to=datetime.datetime.now(), count=25)
        today_open = df.iloc[-1]['close']  # 전날 00:00 종가 = 오늘 시가
        yesterday_high = max(df['high'])
        yesterday_low = min(df['low'])
        target[ticker] = today_open + (yesterday_high - yesterday_low) * k_value
        time.sleep(0.1)  # json 오류 때문에.

    return target


def get_amount(tickers):
    '''
    전일 변동성을 바탕으로 당일 투자할 비중을 정해주는 메소드.
    :param tickers: (list) 티커들의 리스트
    :return: (dict) 키=티커 / 아이템=투자비중
    '''
    amount = dict()

    for ticker in tickers:
        df = pyupbit.get_ohlcv(ticker, interval='minute60', to=datetime.datetime.now(), count=25)
        yday = df.iloc[0]  # 어제 00:00
        delta = abs(max(df['high']) - min(df['low'])) / yday['close']
        tgt = 0.02  # percentage
        ptg = (tgt / delta)/len(tickers)
        amount[ticker] = min(ptg, 1/6)
        time.sleep(0.1)  # json 오류 때문에.

    return amount


def select_coin(num, major_list):  # 15초 정도 걸림.
    '''
    3대장 + 그날 투자할 랜덤 세개 뽑아주는 메소드
    :param num: (int) 투자할 종목 수.
    :param major_list: (list) 메이저 코인 목록
    :return: (list) 투자할 코인 목록
    '''
    tickers = pyupbit.get_tickers(fiat='KRW')

    candidate = list()
    major = 0
    minor = 0
    for ticker in tickers:

        df = pyupbit.get_ohlcv(ticker, interval='minute60', to=datetime.datetime.now())
        time.sleep(0.1)  # 호출시간 에러
        total = 0

        for i in range(5):
            total += df['close'][-1-24*i]
        moving_avg = total / 5

        if pyupbit.get_current_price(ticker) > moving_avg:
            if ticker in major_list:
                candidate.insert(0, ticker)  # 머리부분에 메이져들 배치
                major += 1
            else:
                candidate.append(ticker)
                minor += 1

    if len(candidate) > num:
        candidate.reverse()  # 메이저 삼대장은 맨 뒤 세군데.
        save = list()
        for i in range(major):
            save.append(candidate.pop())
        candidate = random.sample(candidate, num - major)
        candidate = candidate + save

    return candidate


def renew(user, user_account):

    for currency in user_account:  # 계좌 완전히 리셋

        if currency['currency'] != 'KRW':
            user.sell_market_order("KRW-" + currency['currency'], currency['balance'])
            time.sleep(0.2)  # json error 대비

