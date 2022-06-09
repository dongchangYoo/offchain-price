from dataclasses import dataclass, field
from typing import Optional

from dataclasses_json import LetterCase, dataclass_json


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class Coin:
    id: str
    symbol: str
    name: str = field(repr=False)
    market_data: dict = field(repr=False)
    last_updated: str  # TODO
    block_time_in_minutes: Optional[float] = field(repr=False)

    # ignored field..
    # image: dict
    # localization: dict  # national notation

    # parsed members
    prices: list = field(init=False)
    market_cap: int = field(init=False)
    market_cap_change_percentage_24h: float = field(init=False)
    total_volume: int = field(init=False)
    total_supply: int = field(init=False)
    circulating_supply: int = field(init=False)
    price_change_percentages: dict = field(init=False)

    def __post_init__(self):
        self.prices = [
            self.market_data["current_price"]["usd"],
            self.market_data["high_24h"]["usd"],
            self.market_data["low_24h"]["usd"],
        ]

        self.market_cap = self.market_data["market_cap"]["usd"]  # 거래량
        self.market_cap_change_percentage_24h = self.market_data["market_cap_change_percentage_24h"]

        self.total_volume = self.market_data["total_volume"]["usd"]  # 시가 총액
        self.total_supply = self.market_data["total_supply"]  # 발행량
        self.circulating_supply = self.market_data["circulating_supply"]  # 유통량

        self.price_change_percentages = {
            "1h": self.market_data["price_change_percentage_1h_in_currency"]["usd"],
            "24h": self.market_data["price_change_percentage_24h"],
            "7d": self.market_data["price_change_percentage_7d"],
            "14d": self.market_data["price_change_percentage_14d"],
            "30d": self.market_data["price_change_percentage_30d"],
            "60d": self.market_data["price_change_percentage_60d"],
            "200d": self.market_data["price_change_percentage_200d"],
            "1y": self.market_data["price_change_percentage_1y"]
        }
