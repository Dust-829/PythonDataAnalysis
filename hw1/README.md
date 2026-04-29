# Homework 1: Scrapy Stock Data Crawler

## 作业目标

使用 Scrapy 爬取股票行情数据，并将结果保存到 CSV 文件和 MySQL 数据库中。数据源使用东方财富行情接口，字段包括股票代码、名称、最新价、涨跌幅、成交量、成交额等。

## 目录说明

- `src/stock_spider/`: Scrapy 项目源码
- `data/`: CSV 输出目录
- `sql/create_table.sql`: MySQL 建库建表脚本
- `report/`: Word 报告模板

## 安装依赖

```powershell
cd D:\work\PythonDataAnalysis\hw1
python -m pip install -r requirements.txt
```

安装完成后，当前项目会以可编辑模式安装，`scrapy crawl eastmoney_stock` 才能正确找到 `src/stock_spider` 包。

## 初始化 MySQL

先登录 MySQL，然后执行：

```sql
SOURCE D:/work/PythonDataAnalysis/hw1/sql/create_table.sql;
```

如果你的 MySQL 不支持 `SOURCE`，可以打开 `sql/create_table.sql`，复制其中 SQL 语句执行。

## 配置 MySQL 连接

PowerShell 示例：

```powershell
$env:MYSQL_HOST="localhost"
$env:MYSQL_PORT="3306"
$env:MYSQL_USER="root"
$env:MYSQL_PASSWORD="你的MySQL密码"
$env:MYSQL_DATABASE="python_data_analysis"
```

## 运行爬虫

```powershell
cd D:\work\PythonDataAnalysis\hw1
scrapy crawl eastmoney_stock
```

运行后会生成：

- CSV 文件：`data/stocks.csv`
- MySQL 表：`python_data_analysis.stock_quotes`

## 建议截图

- 依赖安装成功截图
- MySQL 建表成功截图
- Scrapy 运行过程截图
- `data/stocks.csv` 打开后的结果截图
- MySQL 查询 `SELECT * FROM stock_quotes LIMIT 10;` 的结果截图
