import requests, json, numpy, os
import pandas as pd
import yahoo_fin as yf
from datetime import datetime
import yahoo_fin.stock_info as si
import yahoo_fin.options as op
import matplotlib.pyplot as plt
import seaborn as sns
url = "https://rtstockdata.azurewebsites.net/request"
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

    def get_historical(self,ticker,start,end,interval):
        df = pd.DataFrame
        try:
            df = si.get_data(ticker, start_date=start, end_date=end, index_as_date=False, interval=interval)
        except Exception as e:
            print(e)
        return df

    def get(self, ticker, start, end, pandas=False, interval='1min'):

        # Make requests and get server response
        response = requests.get(url, headers=headers,
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

        # Check if user didn't input a list
        if isinstance(tickers, str):
            return ValueError("Please use a list of tickers instead of just one. Ex: ['MSFT']")

        # Graph price or percent
        if graphType == 'price':
            for ticker in tickers:
                raw_data = self.get(ticker, start, end, interval=interval)
                times = [datetime.strptime(time, '%Y-%m-%d %H:%M:%S') for time in raw_data.keys()]
                prices = [raw_data[time] for time in raw_data.keys()]
                plt.plot(times, prices, label=ticker)
        else:
            for ticker in tickers:
                try:
                    interval_num = int(interval[0:len(interval) - 1])
                except:
                    raise ValueError("Please enter the right interval value.")

                if interval[len(interval) - 1:] == 'm':
                    raw_data = self.get(ticker, start, end, pandas=True)
                    for i in range(0, len(raw_data.index)):
                        if i % interval_num != 0:
                            raw_data.drop(i, axis=0, inplace=True)
                    plt.plot(raw_data['time'], raw_data['price'], label=ticker)
                elif interval[1:] == 'd':
                    raw_data = self.get_historical(ticker, start, end,"1d")
                    for i in range(0, len(raw_data.index)):
                        if i % interval_num != 0:
                            raw_data.drop(i, axis=0, inplace=True)
                    plt.plot(raw_data['date'], raw_data['adjclose'], label=ticker)
                else:
                    raise ValueError("Please enter the right interval value.")
        plt.title("Stock Data")
        plt.ylabel('Price')
        plt.xlabel('Time (' + interval + ')')
        plt.legend()
        plt.show()
        plt.close()

    def export_CSV(self, ticker, start, end):
        data = self.get(ticker, start, end, True)
        return data.to_csv("C:\\Users\\" + os.getlogin() + "\\Desktop\\" + ticker + ".csv", index=False)

stock = Stocket("JOkuFdOZsmINV3od9vfB3WutuDKc13ED2GcNiCIM")
#stock.graph(['AAPL'], "08/19/2020", "09/18/2020", interval="1d")
stock.graph(['MSFT'], "2020-09-17 10:00", "2020-09-18 16:00", interval="1m",graphType="price")

