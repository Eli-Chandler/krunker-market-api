from datetime import datetime
from typing import List

from krunker_market_api.models.krunker_message import KrunkerMessage
from dataclasses import dataclass


class ClientItemMarketInfoMessage(KrunkerMessage):
    def __init__(self, item_id: int):
        super().__init__(
            'r',
            [
                "itemsales",
                "market",
                None,
                None,
                None,
                0,
                item_id
            ]
        )


class ServerItemMarketInfoMessage(KrunkerMessage):
    @property
    def item_id(self) -> str:
        return self.data[2]['ind']

    @property
    def high_price(self) -> int:
        return self.data[2]['high']

    @property
    def low_price(self) -> int:
        return self.data[2]['low']

    @property
    def in_circulation(self) -> int:
        return self.data[2]['inC']

    @property
    def on_sale(self) -> int:
        return self.data[2]['onS']


class ClientItemSalesHistoryMessage(KrunkerMessage):
    def __init__(self, item_id: int):
        super().__init__(
            'st',
            [item_id, '6']
        )


class ServerItemSalesHistoryMessage(KrunkerMessage):
    @property
    def item_id(self) -> int:
        return self.data[1]

    @property
    def sales(self) -> List[dict]:
        return self.data[0]


@dataclass
class ItemMarketInfo:
    item_id: str
    high_price: int
    low_price: int
    in_circulation: int
    on_sale: int

    @classmethod
    def from_krunker_message(cls, message: ServerItemMarketInfoMessage) -> 'ItemMarketInfo':
        return cls(
            item_id=message.item_id,
            high_price=message.high_price,
            low_price=message.low_price,
            in_circulation=message.in_circulation,
            on_sale=message.on_sale
        )


@dataclass
class ItemSalesDay:
    item_id: str
    average_price: int
    count: int
    date: datetime

    @staticmethod
    def from_krunker_message(message: ServerItemSalesHistoryMessage) -> List['ItemSalesDay']:
        return [ItemSalesDay(
            item_id=message.data[1],
            average_price=sale['f'],
            count=sale['t'],
            date=datetime.strptime(sale['d'], '%Y-%m-%d')
        ) for sale in message.sales]
