import requests
import datetime
from twilio.rest import Client

# -------- FIRST PIECES OF DATA ------- #
STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"
NEWS_API = "66fd833b6aca489998ce3e2b923675e3"
ALPHAVANTAGE_API = "GE4VJ8J71JIM52HV"
TWILIO_SID = "AC81aad1bee85f1e88250f8504570cd0f6"
TWILIO_AUTH_TOKEN = "cf5b4c1dcbf9908f51c2b7f5292d99e7"


def send_messages(chunk_of_news, coefficient_of_price):
    if coefficient_of_price > 0:
        title = f"{STOCK}: 🔺{round(coefficient_of_price, 2) * 100}%"
    else:
        title = f"{STOCK}: 🔻{round(coefficient_of_price, 2) * 100}%"
    headline = f"Headline: {chunk_of_news['title']}"
    brief = f"Brief: {chunk_of_news['description'][:200]}"
    final_message = f"{title}\n\n{headline}\n\n{brief}..."
    client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)
    message = client.messages \
        .create(
        body=final_message,
        from_='+13185350660',
        to='+380500879746'
    )
    print(message.sid)


parameters_alphaventage = {
    "function": "TIME_SERIES_INTRADAY",
    "symbol": STOCK,
    "interval": "60min",
    "datatype": "json",
    "apikey": ALPHAVANTAGE_API
}

answer_from_alphaventage = requests.get("https://www.alphavantage.co/query", params=parameters_alphaventage)
answer_from_alphaventage.raise_for_status()
json_alphavantage = answer_from_alphaventage.json()

# time manipulation (yesterday and before yesterday in a string format)
today = datetime.datetime.now()
yesterday = today - datetime.timedelta(days=1)
before_yesterday = today - datetime.timedelta(days=2)
yesterday = str(yesterday.date())
before_yesterday = str(before_yesterday.date())

# geting info from dictionary
stock_data_yesterday = json_alphavantage["Time Series (60min)"]["%s 20:00:00" % (yesterday,)]["1. open"]
stock_data_before_yesterday = json_alphavantage["Time Series (60min)"]["%s 20:00:00" % (before_yesterday,)]["1. open"]
stock_data_yesterday = float(stock_data_yesterday)
stock_data_before_yesterday = float(stock_data_before_yesterday)

# calc
delta = stock_data_yesterday - stock_data_before_yesterday
coefficient_of_price_change = delta / stock_data_yesterday
if abs(coefficient_of_price_change) > 0.01:
    parameters_newsapi = {
        "q": COMPANY_NAME,
        "from": before_yesterday,
        "to": yesterday,
        "language": 'en',
        "sort_by": 'relevancy',
        "apiKey": NEWS_API,
    }

    answer_from_newsapi = requests.get("https://newsapi.org/v2/everything", params=parameters_newsapi)
    answer_from_newsapi.raise_for_status()
    print(answer_from_newsapi)
    news_json = answer_from_newsapi.json()
    top3_news = news_json["articles"][0:3]
    for i in range(3):
        send_messages(top3_news[i], coefficient_of_price=coefficient_of_price_change)

# Format the SMS message example:
"""
TSLA: 🔺2%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file
by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the 
coronavirus market crash.
or
"TSLA: 🔻5%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to 
file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of
the coronavirus market crash.
"""
