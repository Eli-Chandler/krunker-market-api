from datetime import datetime
from typing import List

from krunker_market_api.models.krunker_message import KrunkerMessage, KrunkerRequest, T
from dataclasses import dataclass

from krunker_market_api.models.user import LoggedInDetails


class MarketInfoRequest(KrunkerRequest["ServerItemMarketInfoMessage"]):
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

    def matches(self, message: "KrunkerMessage") -> bool:
        return message.message_type == '0' and len(message.data) >= 2 and message.data[0] == 'itemsales' and message.data[1] == 'market'

    @property
    def response_type(self):
        return ServerItemMarketInfoMessage


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


class ItemSalesHistoryRequest(KrunkerRequest["ServerItemSalesHistoryMessage"]):
    def __init__(self, item_id: int):
        self._item_id = item_id

        super().__init__(
            'st',
            [item_id, '6']
        )

    def matches(self, message: "KrunkerMessage") -> bool:
        return message.message_type == 'gd' and len(message.data) >= 1 and message.data[1] == self._item_id

    @property
    def response_type(self) -> type[T]:
        return ServerItemSalesHistoryMessage


class ServerItemSalesHistoryMessage(KrunkerMessage):
    @property
    def item_id(self) -> int:
        return self.data[1]

    @property
    def sales(self) -> List[dict]:
        return self.data[0]

# [
#     "r",
#     "market",
#     "market",
#     "310032",
#     ".Floow",
#     null,
#     0,
#     "1075"
# ]

class ItemListingsRequest(KrunkerRequest["ItemListingsResponse"]):
    def __init__(self, item_id: str, identity: LoggedInDetails):
        self._item_id = item_id
        super().__init__(
            message_type="r",
            data=[
                "market",
                "market",
                identity.id,
                identity.username,
                None,
                0,
                item_id
            ]
        )

    def matches(self, message: KrunkerMessage) -> bool:
        if message.message_type != "fr":
            return False

        if len(message.data) < 2:
            return False

        if not isinstance(message.data[1], list):
            return False

        listings: list = message.data[1]

        if len(listings) == 0:
            # If there are no listings we kinda just have to guess what request this was for
            # Hopefully websocket ordering should take care of this
            # But there could still be race conditions on krunkers end
            # i.e. we make request a, b, and their servers figure out b first and send it back on the websocket first
            # we could enforce some locking with rate limiting if this becomes an issue i.e. 50ms timeout, although not ideal
            return True

        if not isinstance(listings[0], dict):
            return False

        # request item_id is str but response is int el classico good api design
        if str(listings[0]["sx"]) != self._item_id:
            return False

        return True

    @property
    def response_type(self) -> type["ItemListingsResponse"]:
        return ItemListingsResponse

@dataclass(frozen=True)
class KrunkerItemListing:
    item_id: str
    listing_id: str
    owner_username: str
    sale_start: datetime
    price: int

class ItemListingsResponse(KrunkerMessage):
    @property
    def listings(self) -> list[KrunkerItemListing]:
        raw_listings: list[dict] = self.data[1]
        listings = [
            KrunkerItemListing(
                item_id=raw_listing["sx"],
                listing_id=raw_listing["m"],
                owner_username=raw_listing["p"],
                sale_start=datetime.fromtimestamp(int(raw_listing["salestart"]) / 1000),
                price=raw_listing["f"]
            )
            for raw_listing in raw_listings
        ]

        listings.sort(key=lambda l: l.price)
        return listings

class PurchaseListingRequest(KrunkerRequest["ListingPurchaseResponse"]):
    def __init__(self, listing_id: str):
        self._listing_id = int(listing_id)
        super().__init__(
            message_type="pi",  # yeah, IDK krunker uses the same message as ping to buy items
            data=[
                int(listing_id),
                0
            ]
        )

    def matches(self, message: KrunkerMessage) -> bool:
        return message.message_type == "br" and len(message.data) >=1 and isinstance(message.data[0], dict) and message.data[0].get("mid") == self._listing_id

    @property
    def response_type(self) -> type["ListingPurchaseResponse"]:
        return ListingPurchaseResponse

# [
#     "br",
#     {
#         "f": 2546,
#         "sid": 142102045,
#         "mid": 34772738,
#         "skn": 3241
#     },
#     0
# ]
class ListingPurchaseResponse(KrunkerMessage):
    pass


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
