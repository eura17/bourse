import requests

api = 'http://127.0.1.1:5000/api/simulation/run'

data = {
    'tickers': ['AFLT'],
    'dates': ['2015-12-10', '2015-12-11'],
    'strategies': {
        'MACD': {
            'fast_period': 16,
            'slow_period': 26,
            'signal_period': 9,
            'periodicity': '1m'
        },
        'MACD_EMA': {
            'fast_period': 16,
            'slow_period': 26,
            'signal_period': 9,
            'periodicity': '1m'
        },
        'RSI': {
            'RSI_period': 14,
            'periodicity': '1m'
        },
        'LSTM': {
            'lookback_period': 30,
            'forecast_period': 22
        }
    },
    'start_account': 100000,
    'leverage': 3,
    'commission_abs': 0,
    'commission_pct': 0,
    'discreteness': 1,
    'port': 4442,
}

requests.post(api, data=data)