import requests, json

url = "https://rtstockdata.azurewebsites.net/request"
headers = {'Content-Type': "application/json", 'Accept': "application/json"}


def get(ticker, start, end):
    response = requests.get(url, headers = headers, json = {'ticker': ticker, 'start': start, 'end': end})
    parsed = {}
    for pair in response.json()['recordsets'][0]:
        parsed.update({pair['datetime']: pair['price']})
    return parsed

print(get('A', "", ""))