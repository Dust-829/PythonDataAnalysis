# Homework 2: Pandas Stock Data Analysis

## Overview

This homework is independent from `hw1`.

It follows the workflow shown in the assignment images:

1. Prepare the Python environment
2. Download real stock history data from Yahoo Finance with `yfinance`
3. Clean the data with `pandas`
4. Visualize the price trend
5. Compute technical indicators: `SMA` and `RSI`
6. Perform deeper analysis: returns and volatility

The default stock in this project is `600519.SS` (Kweichow Moutai) and the default date range is `2024-01-01` to `2024-12-31`.

## Install Dependencies

```powershell
cd D:\work\PythonDataAnalysis\hw2
python -m pip install -r requirements.txt
```

## Run Analysis

```powershell
cd D:\work\PythonDataAnalysis\hw2
python src\run_analysis.py
```

## Output Files

- `data/raw_600519_SS_2024.csv`: raw Yahoo Finance history data
- `data/cleaned_600519_SS_2024.csv`: cleaned analysis dataset
- `output/close_price.png`: closing price chart
- `output/sma.png`: moving average chart
- `output/rsi.png`: RSI chart
- `output/cumulative_return.png`: cumulative return chart
- `output/analysis_summary.txt`: summary metrics and interpretation
- `report/homework2_report.docx`: Word report

## Suggested Screenshots

- dependency installation in terminal
- `python src\run_analysis.py` execution result in terminal
- raw data preview
- missing value check result
- generated charts
- final metrics in `analysis_summary.txt`
