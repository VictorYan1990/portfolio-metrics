import requests
from enum import Enum
from datetime import date
from util.logger import logger
from app.core.config import settings


class APIPriceType(Enum):
    adjusted_close = "5. adjusted close"
    close = "4. close"
    open = "1. open"
    high = "2. high"
    low = "3. low"


class PriceHandler(object):

    def __init__(self, api_settings: settings.InstrumentAPI_Settings):
        self.api_settings = api_settings
        self.params = {
            "function": "TIME_SERIES_DAILY",
            "apikey": self.api_settings.api_key,
            "outputsize": "compact"
        }

    def get_price(self, symbol: str, as_of_date: date, price_type: APIPriceType) -> float:

        self.params["symbol"] = symbol
        # Send request
        response = requests.get(self.api_settings.url, params=self.params)
        data = response.json()

        logger.info(f"raw response price Data: {data}")
        return data["Time Series (Daily)"][as_of_date][price_type.value]
