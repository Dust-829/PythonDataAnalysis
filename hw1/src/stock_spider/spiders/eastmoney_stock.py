import json
from datetime import datetime

import scrapy

from stock_spider.items import StockItem


class EastmoneyStockSpider(scrapy.Spider):
    name = "eastmoney_stock"
    allowed_domains = ["eastmoney.com"]

    custom_settings = {
        "FEED_EXPORT_FIELDS": [
            "code",
            "name",
            "latest_price",
            "change_percent",
            "change_amount",
            "volume",
            "turnover",
            "amplitude",
            "high",
            "low",
            "open_price",
            "previous_close",
            "market",
            "crawl_time",
        ]
    }

    def start_requests(self):
        params = {
            "pn": "1",
            "pz": "80",
            "po": "1",
            "np": "1",
            "fltt": "2",
            "invt": "2",
            "fid": "f3",
            "ut": "bd1d9ddb04089700cf9c27f6f7426281",
            "fs": "m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23",
            "fields": "f2,f3,f4,f5,f6,f7,f12,f14,f15,f16,f17,f18,f100",
        }
        query = "&".join(f"{key}={value}" for key, value in params.items())
        yield scrapy.Request(
            url=f"https://push2.eastmoney.com/api/qt/clist/get?{query}",
            callback=self.parse,
        )

    def parse(self, response):
        payload = json.loads(response.text)
        stocks = payload.get("data", {}).get("diff", [])
        if not stocks:
            self.logger.warning("No stock rows found. Response preview: %s", response.text[:300])
            return

        crawl_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        for stock in stocks:
            yield StockItem(
                code=stock.get("f12"),
                name=stock.get("f14"),
                latest_price=self._none_if_dash(stock.get("f2")),
                change_percent=self._none_if_dash(stock.get("f3")),
                change_amount=self._none_if_dash(stock.get("f4")),
                volume=self._none_if_dash(stock.get("f5")),
                turnover=self._none_if_dash(stock.get("f6")),
                amplitude=self._none_if_dash(stock.get("f7")),
                high=self._none_if_dash(stock.get("f15")),
                low=self._none_if_dash(stock.get("f16")),
                open_price=self._none_if_dash(stock.get("f17")),
                previous_close=self._none_if_dash(stock.get("f18")),
                market=stock.get("f100"),
                crawl_time=crawl_time,
            )

    @staticmethod
    def _none_if_dash(value):
        if value == "-":
            return None
        return value
