import requests

def get_top_coins():

    url = (
        "https://api.coingecko.com/api/v3/coins/markets"
        "?vs_currency=usd"
        "&order=market_cap_desc"
        "&per_page=20"
        "&page=1"
        "&sparkline=false"
    )

    response = requests.get(url)

    if response.status_code == 200:
        return response.json()

    return []

def get_coin_history(coin_id, days=30):

    url = (
        f"https://api.coingecko.com/api/v3/coins/"
        f"{coin_id}/market_chart"
        f"?vs_currency=usd&days={days}"
    )

    response = requests.get(url)

    if response.status_code == 200:
        return response.json()

    return None