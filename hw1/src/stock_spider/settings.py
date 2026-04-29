BOT_NAME = "stock_spider"

SPIDER_MODULES = ["stock_spider.spiders"]
NEWSPIDER_MODULE = "stock_spider.spiders"

ROBOTSTXT_OBEY = False
DOWNLOAD_DELAY = 1
CONCURRENT_REQUESTS = 4
LOG_LEVEL = "INFO"

DEFAULT_REQUEST_HEADERS = {
    "Accept": "application/json,text/plain,*/*",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Referer": "https://quote.eastmoney.com/center/gridlist.html",
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0 Safari/537.36"
    ),
}

FEEDS = {
    "data/stocks.csv": {
        "format": "csv",
        "encoding": "utf-8-sig",
        "overwrite": True,
        "fields": [
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
        ],
    }
}

ITEM_PIPELINES = {
    "stock_spider.pipelines.MySQLPipeline": 300,
}

