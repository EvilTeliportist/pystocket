# pystocket (https://rtstockdata.azurewebsites.net/)

Stocket is a lightweight finance API designed to provide quick and easy access to SMP500 stock market data. We use an Node.js server connected to an SQL database, and update the database every minute through a separate application using asynchronous requests to avoid clogging the main web server. Our main implementation, PyStocket can be installed as a Python package. Please view the documentation on the GitHub, and review the usage parameters before using. Improper use could result in the automated deactivation of your token. Stocket is not meant to be the fastest or most expansive API, but aims to provide beginners with a simple source of stock market data down to per minute increments, so that anybody interested in quantitative finance can easily get started with comprehensible data.

Stocket is very early in development, and is only being supported by two freshman college students, but a working version has been established. Please bear with us on any bug fixes or design changes that need to happen. 

Lastly, please remember that this API updates itself, and only has data back until the API conception on September 17, 2020. In the Python package, we can provide end of day (EOD) data from quite a while ago using another API, but our minute data only dates back to September of 2020.

Thank you, and happy trading!

# Installation

``` pip install pystocket ```

# Example Usage
```
from pystocket import Stocket

stocket = Stocket('<your token here>')

print(stocket.get('MSFT', '2020-09-17 09:38', '2020-09-17 09:50'))
```

## Available Methods - *required

get() - simple get method, requests from API
- ticker*: string ("MSFT")
- start*: string (see formatting above)
- end*: string (see formatting above)
- pandas: bool (defaults false)
- interval: string (defaults '1min')(formatting: 'int + min/hr')


graph() - matplotlib graph of ticker percentage growth
- tickers*: list of strings (["AAPL"])
- start*: string (see formatting above)
- end*: string (see formatting above)
- interval: string (defaults '1min')(formatting: 'int + min/hr')
- type: defaults to percentage
- - "percentage": shows percentage growth from first day requested
- - "price": shows price of ticker

exportToCSV() - exports data to CSV file
- tickers*: string ("TSLA")
- start*: string (see formatting above)
- end*: string (see formatting above)

setToken() - sets token
- token*: string

dividends() - gets all dividends data
- no args