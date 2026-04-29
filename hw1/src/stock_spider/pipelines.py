import os

import pymysql


class MySQLPipeline:
    def __init__(self):
        self.connection = None
        self.cursor = None

    def open_spider(self, spider):
        password = os.getenv("MYSQL_PASSWORD")
        if not password:
            spider.logger.warning("MYSQL_PASSWORD is not set; MySQL saving is skipped.")
            return

        self.connection = pymysql.connect(
            host=os.getenv("MYSQL_HOST", "localhost"),
            port=int(os.getenv("MYSQL_PORT", "3306")),
            user=os.getenv("MYSQL_USER", "root"),
            password=password,
            database=os.getenv("MYSQL_DATABASE", "python_data_analysis"),
            charset="utf8mb4",
            autocommit=False,
        )
        self.cursor = self.connection.cursor()

    def process_item(self, item, spider):
        if not self.connection:
            return item

        sql = """
            INSERT INTO stock_quotes (
                code, name, latest_price, change_percent, change_amount,
                volume, turnover, amplitude, high, low, open_price,
                previous_close, market, crawl_time
            ) VALUES (
                %(code)s, %(name)s, %(latest_price)s, %(change_percent)s,
                %(change_amount)s, %(volume)s, %(turnover)s, %(amplitude)s,
                %(high)s, %(low)s, %(open_price)s, %(previous_close)s,
                %(market)s, %(crawl_time)s
            )
            ON DUPLICATE KEY UPDATE
                name = VALUES(name),
                latest_price = VALUES(latest_price),
                change_percent = VALUES(change_percent),
                change_amount = VALUES(change_amount),
                volume = VALUES(volume),
                turnover = VALUES(turnover),
                amplitude = VALUES(amplitude),
                high = VALUES(high),
                low = VALUES(low),
                open_price = VALUES(open_price),
                previous_close = VALUES(previous_close),
                market = VALUES(market)
        """
        self.cursor.execute(sql, dict(item))
        return item

    def close_spider(self, spider):
        if self.connection:
            self.connection.commit()
            self.cursor.close()
            self.connection.close()

