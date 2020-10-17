import requests, json, numpy, os
import pandas as pd
from datetime import datetime
import yahoo_fin as yf
import yahoo_fin.stock_info as si
import yahoo_fin.options as op
import matplotlib.pyplot as plt

url = "https://rtstockdata.azurewebsites.net/"
headers = {'Content-Type': "application/json", 'Accept': "application/json"}


class TokenError(Exception):
    pass


class Stocket():
    def __init__(self, token):
        self.token = token

    def parseTime(self, time, toDatetime = False):
        time = time.replace("T", " ")[:-5]
        if toDatetime:
            return datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
        else:
            return time
         
    def get(self, ticker, start, end, pandas=False, interval='1min'):

        # Make requests and get server response
        response = requests.get(url + 'request', headers=headers,
                                json={'ticker': ticker, 'start': start, 'end': end, 'token': self.token})

        respJson = response.json()['message']

        # Error checking
        if respJson == 'bad chars':
            raise ValueError(
                "Please exclude quotation characters and semicolons from your queries. This helps protect us from SQL injection attacks.")

        if respJson == 'Invalid Token':
            raise TokenError("Invalid API Token")

        if respJson == 'Invalid Ticker':
            raise ValueError("Invalid ticker. This ticker is not supported in Stocket.")

        if start < '2020-09-17 09:35' or end > datetime.now().strftime('%Y-%m-%d %H:%m'):
            raise ValueError("Invalid date. Please enter a start date after 2020-09-17 09:35")

        
        # Get raw minute data
        parsed = {}
        for pair in response.json()['data']['recordsets'][0]:
            parsed.update({self.parseTime(pair['dt']): pair['price']})

        intervalDelimiter = 1
        # Parse data into required interval
        if 'min' in interval:
            try:
                intervalDelimiter = int(interval.replace("min", ""))
                if intervalDelimiter < 0 or intervalDelimiter > 59:
                    raise ValueError("Invalid value for interval. Please see documentation.")
            except:
                raise ValueError("Invalid value for interval. Please see documentation.")

        if 'hr' in interval:
            try:
                intervalDelimiter = 60 * int(interval.replace("hr", ""))
                if intervalDelimiter > 390 or intervalDelimiter < 0:
                    raise ValueError("Invalid value for period. Please see documentation.")
            except:
                raise ValueError("Invalid value for period. Please see documentation.")

        if intervalDelimiter != 1:
            index = 0
            temp_data = {}
            for key in parsed.keys():
                if index % intervalDelimiter == 0:
                    temp_data.update({key: parsed[key]})
                    index += 1
                else:
                    index += 1
            parsed = temp_data


        # Convert to pandas dataframe if need be
        if pandas:
            parsedprice = pd.Series(list(parsed.values()), name='price')
            parsedtime = pd.Series(list(parsed.keys()), name='time')
            frame = {'time': parsedtime, 'price': parsedprice}
            df = pd.DataFrame(frame)
            return df

        return parsed

    def graph(self, tickers, start, end, interval="1m", graphType="percentage"):
        width = 12
        height = 10
        plt.figure(figsize=(width, height))
        for ticker in tickers:
            raw_data = self.get(ticker, start, end, pandas=True)
            try:
                interval_num = int(interval[0:len(interval) - 1])
            except:
                raise ValueError("Please enter the right interval value.")

            # elif interval[1:] == 'd': - When eod table/data added
            if interval[len(interval) - 1:] == 'm':
                for i in range(0, len(raw_data.index)):
                    if i % interval_num != 0:
                        raw_data.drop(i, axis=0, inplace=True)
            else:
                raise ValueError("Please enter the right interval value.")
            plt.plot(raw_data['time'], raw_data['price'], label=ticker)
        plt.title("Stock Data")
        plt.ylabel('Price')
        plt.xlabel('Time (' + interval + ')')
        plt.legend()
        plt.show()
        plt.close()

    def exportToCSV(self, ticker, start, end):
        data = self.get(ticker, start, end, pandas=True)
        return data.to_csv("C:\\Users\\" + os.getlogin() + "\\Desktop\\" + ticker + ".csv", index=False)

    def setToken(self, token):
        self.token = token

    def dividends(self):
        return requests.get(url + 'dividends', headers=headers, json={'token':self.token}).json()

