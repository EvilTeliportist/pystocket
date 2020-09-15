import requests, json, numpy
import pandas as pd

url = "https://rtstockdata.azurewebsites.net/request"
headers = {'Content-Type': "application/json", 'Accept': "application/json"}

class TokenError(Execption):
    pass

def get(ticker, start, end, token = "", pandas = False):
    response = requests.get(url, headers = headers, json = {'ticker': ticker, 'start': start, 'end': end, 'token': token}).json()
    
    if response['message'] == 'bad chars':
        raise ValueError("Please exclude quotation characters and semicolons from your queries. This helps protect us from SQL injection attacks.")
    
    if response['message'] == 'Invalid Token':
        raise TokenError("Invalid API Token")

    parsed = {}
    for pair in response.json()['data']['recordsets'][0]:
        parsed.update({pair['datetime']: pair['price']})

    if pandas:
        parsed = pd.Series(parsed, name = 'price')
        parsed.index.name = 'time'
        parsed.reset_index()
        return parsed

    return parsed

data = get('MSFT', "", "", pandas=True)
print(data)