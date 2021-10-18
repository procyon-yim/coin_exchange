import pyupbit
import time
import datetime
import smtplib
from email.mime.text import MIMEText
import random
import gspread
from oauth2client.service_account import ServiceAccountCredentials


def send_alarm(mail_info, text):
    '''
    이메일 보내주는 메소드
    :param mail_info: (str) 메일 보내는 주소, 받는 주소, 보내는 주소의 비밀번호가 담긴 텍스트 파일 이름
    :param text: (str) 보낼 메세지
    :return: None
    '''
    with open(mail_info) as f:
        file = f.readlines()
        sendEmail = file[0][:-1]
        password = file[1][:-1]
        recvEmail = file[2]

    smtpName = "smtp.naver.com"  # smtp server address
    smtpPort = 587  # smtp port number

    msg = MIMEText(text)  # MIMEText(text , _charset = "utf8")

    msg['Subject'] = "Coin Exchanger's Report"
    msg['From'] = sendEmail
    msg['To'] = recvEmail

    s = smtplib.SMTP(smtpName, smtpPort)  # connecting to email server
    s.starttls()  # TLS security
    s.login(sendEmail, password)  # login
    s.sendmail(sendEmail, recvEmail, msg.as_string())  # sending an email
    s.close()  # terminating smtp server connection
    time.sleep(1)


def get_target_price(tickers, k_value):
    '''
    This is a method that returns a target price of currencies, based on Larry Williams's Volatility breakout strategy
    :param tickers: (list) a list of tickers (e.g. 'BTC-KRW')
    :param k_value: (float) breakout coefficient
    :return: (dict) keys = tickers, values = target price
    '''

    target = dict()

    for ticker in tickers:

        df = pyupbit.get_ohlcv(ticker, interval='minute60', to=datetime.datetime.now(), count=25)
        today_open = df.iloc[-1]['close']
        yesterday_high = max(df['high'])
        yesterday_low = min(df['low'])
        target[ticker] = today_open + (yesterday_high - yesterday_low) * k_value
        time.sleep(0.1)

    return target


def get_amount(tickers):
    '''
    This method returns an amount of current balance to be invested, based on yesterday's fluctuation range.
    :param tickers: (list) a list of tickers
    :return: (dict) keys = tickers, values = amount to be invested
    '''
    amt = dict()

    for ticker in tickers:

        df = pyupbit.get_ohlcv(ticker, interval='minute60', to=datetime.datetime.now())
        time.sleep(0.1)
        total = 0
        for i in range(5):
            total += df['close'][-1-24*i]
        mov5 = total / 5

        current_price = pyupbit.get_current_price(ticker)
        if current_price > mov5:

            yday = df.iloc[-25]
            delta = abs(max(df.iloc[-25:]['high']) - min(df.iloc[-25:]['low'])) / yday['close']
            tgt = 0.02
            ptg = (tgt / delta)/len(tickers)
            amt[ticker] = min(ptg, 1/len(tickers))

        else:
            amt[ticker] = 0

        time.sleep(0.1)

    return amt


def select_coin(num, major_list):
    '''
    Obsolete method
    3대장 + 그날 투자할 랜덤 세개 뽑아주는 메소드 (8월 26일부로 안씀)
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
    '''
    This method renews the user's balance every 00:00
    :param user: (class: Upbit) user's account
    :param user_account: (dict) user's balance. (user.get_balances())
    :return: None.
    '''
    for currency in user_account:

        if currency['currency'] != 'KRW':
            user.sell_market_order("KRW-" + currency['currency'], currency['balance'])
            time.sleep(0.2)


def login(login_info):

    with open(login_info) as f:
        keys = f.readlines()
        access_key = keys[0][:-1]
        secret_key = keys[1]

    return access_key, secret_key


def logger(google_info, balance):
    '''
    구글 스프레드시트에 매일 자산 현황을 업데이트 해주는 메소드
    :param google_info: json 파일
    :param balance: 현재 자산
    :return:
    '''
    scope = [
        'https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive',
    ]
    json_file_name = google_info
    credentials = ServiceAccountCredentials.from_json_keyfile_name(json_file_name, scope)
    gc = gspread.authorize(credentials)
    spreadsheet_url = 'https://docs.google.com/spreadsheets/d/1Cs8FipYPmQqGY8wB3MvPNIH7iJ5xrqutslQK2IzhfeM/edit#gid=0'
    # 스프레스시트 문서 가져오기
    doc = gc.open_by_url(spreadsheet_url)
    # 시트 선택하기
    worksheet = doc.worksheet('data')
    now = datetime.datetime.now()
    date = str(now.year)+'/'+str(now.month)+'/'+str(now.day)
    worksheet.update_cell(now.day, now.month*2-1, date)
    worksheet.update_cell(now.day, now.month*2, str(balance))
