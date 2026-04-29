import scrapy


class StockItem(scrapy.Item):
    code = scrapy.Field()
    name = scrapy.Field()
    latest_price = scrapy.Field()
    change_percent = scrapy.Field()
    change_amount = scrapy.Field()
    volume = scrapy.Field()
    turnover = scrapy.Field()
    amplitude = scrapy.Field()
    high = scrapy.Field()
    low = scrapy.Field()
    open_price = scrapy.Field()
    previous_close = scrapy.Field()
    market = scrapy.Field()
    crawl_time = scrapy.Field()

