import requests, json, numpy
import pandas as pd

url = "https://rtstockdata.azurewebsites.net/request"
headers = {'Content-Type': "application/json", 'Accept': "application/json"}

class TokenError(Exception):
    pass

class Stocket():

    def __init__(self, token):
        self.token = token

    def get(self, ticker, start, end, pandas = False):
        response = requests.get(url, headers = headers, json = {'ticker': ticker, 'start': start, 'end': end, 'token': self.token})
        
        if response.json()['message'] == 'bad chars':
            raise ValueError("Please exclude quotation characters and semicolons from your queries. This helps protect us from SQL injection attacks.")
        
        if response.json()['message'] == 'Invalid Token':
            raise TokenError("Invalid API Token")

        parsed = {}
        for pair in response.json()['data']['recordsets'][0]:
            parsed.update({pair['dt']: pair['price']})

        if pandas:
            parsed = pd.Series(parsed, name = 'price')
            parsed.index.name = 'time'
            parsed.reset_index()
            return parsed

        return parsed