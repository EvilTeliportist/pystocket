import requests, json, numpy, os
import pandas as pd
import yahoo_fin as yf
import yahoo_fin.stock_info as si
import yahoo_fin.options as op
import matplotlib.pyplot as plt

url = "https://rtstockdata.azurewebsites.net/request"
headers = {'Content-Type': "application/json", 'Accept': "application/json"}


class TokenError(Exception):
    pass


class Stocket():
    def __init__(self, token):
        self.token = token

    def get(self, ticker, start, end, pandas=False):
        response = requests.get(url, headers=headers,
                                json={'ticker': ticker, 'start': start, 'end': end, 'token': self.token})

        if response.json()['message'] == 'bad chars':
            raise ValueError(
                "Please exclude quotation characters and semicolons from your queries. This helps protect us from SQL injection attacks.")

        if response.json()['message'] == 'Invalid Token':
            raise TokenError("Invalid API Token")

        parsed = {}
        for pair in response.json()['data']['recordsets'][0]:
            parsed.update({pair['dt']: pair['price']})

        if pandas:
            parsedprice = pd.Series(list(parsed.values()), name='price')
            parsedtime = pd.Series(list(parsed.keys()), name='time')
            frame = {'time': parsedtime, 'price': parsedprice}
            df = pd.DataFrame(frame)
            return df

        return parsed

    def compare_graph(self, tickers, start, end, interval="1m"):
        width = 12
        height = 10
        plt.figure(figsize=(width, height))
        for ticker in tickers:
            raw_data = self.get(ticker, start, end,True)
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

    def graph(self, ticker, start, end, interval="1m"):
        width = 12
        height = 10
        plt.figure(figsize=(width, height))
        raw_data = self.get(ticker, start, end, True)
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
        print(raw_data)
        plt.title("Stock Data")
        plt.plot(raw_data['time'], raw_data['price'], label=ticker)
        plt.ylabel('Price')
        plt.xlabel('Time (' + interval + ')')
        plt.legend()
        plt.show()
        plt.close()

    def export_CSV(self, ticker, start, end):
        data = self.get(ticker, start, end, True)
        return data.to_csv("C:\\Users\\" + os.getlogin() + "\\Desktop\\" + ticker + ".csv", index=False)