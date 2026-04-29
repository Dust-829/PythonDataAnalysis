from __future__ import annotations

from pathlib import Path
import json
from datetime import datetime, timezone

import matplotlib.pyplot as plt
import pandas as pd
import requests
import seaborn as sns
import yfinance as yf


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
OUTPUT_DIR = ROOT / "output"
REPORT_DIR = ROOT / "report"

TICKER = "600519.SS"
START_DATE = "2024-01-01"
END_DATE = "2024-12-31"


def ensure_dirs() -> None:
    for path in (DATA_DIR, OUTPUT_DIR, REPORT_DIR):
        path.mkdir(parents=True, exist_ok=True)


def flatten_columns(df: pd.DataFrame) -> pd.DataFrame:
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [col[0] for col in df.columns]
    return df


def fetch_data() -> pd.DataFrame:
    try:
        df = yf.download(
            TICKER,
            start=START_DATE,
            end=END_DATE,
            interval="1d",
            auto_adjust=False,
            progress=False,
            threads=False,
        )
        df = flatten_columns(df).reset_index()
        if not df.empty:
            return df
    except Exception as exc:
        print(f"yfinance download failed: {exc}")

    print("Falling back to Yahoo Finance chart API.")
    return fetch_data_from_yahoo_api()


def fetch_data_from_yahoo_api() -> pd.DataFrame:
    start_ts = int(datetime.fromisoformat(START_DATE).replace(tzinfo=timezone.utc).timestamp())
    end_ts = int(datetime.fromisoformat(END_DATE).replace(tzinfo=timezone.utc).timestamp())
    url = (
        f"https://query1.finance.yahoo.com/v8/finance/chart/{TICKER}"
        f"?period1={start_ts}&period2={end_ts}&interval=1d&includeAdjustedClose=true"
    )
    response = requests.get(
        url,
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=20,
    )
    response.raise_for_status()
    payload = response.json()
    result = payload["chart"]["result"][0]

    timestamps = result["timestamp"]
    quote = result["indicators"]["quote"][0]
    adjclose = result["indicators"].get("adjclose", [{}])[0].get("adjclose")

    df = pd.DataFrame(
        {
            "Date": pd.to_datetime(timestamps, unit="s"),
            "Open": quote.get("open"),
            "High": quote.get("high"),
            "Low": quote.get("low"),
            "Close": quote.get("close"),
            "Volume": quote.get("volume"),
            "Adj Close": adjclose if adjclose else quote.get("close"),
        }
    )
    return df


def save_raw_data(df: pd.DataFrame) -> Path:
    raw_path = DATA_DIR / "raw_600519_SS_2024.csv"
    df.to_csv(raw_path, index=False, encoding="utf-8-sig")
    return raw_path


def clean_data(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series, pd.Series]:
    df = df.copy()
    missing_before = df.isnull().sum()
    df = df.ffill().bfill()
    missing_after = df.isnull().sum()

    drop_columns = [col for col in ["Adj Close"] if col in df.columns]
    if drop_columns:
        df = df.drop(columns=drop_columns)

    return df, missing_before, missing_after


def calculate_rsi(close_series: pd.Series, window: int = 14) -> pd.Series:
    delta = close_series.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    avg_gain = gain.rolling(window=window).mean()
    avg_loss = loss.rolling(window=window).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["SMA_20"] = df["Close"].rolling(window=20).mean()
    df["SMA_50"] = df["Close"].rolling(window=50).mean()
    df["RSI_14"] = calculate_rsi(df["Close"], window=14)
    df["Daily_Return"] = df["Close"].pct_change()
    df["Cumulative_Return"] = (1 + df["Daily_Return"]).cumprod()
    return df


def save_cleaned_data(df: pd.DataFrame) -> Path:
    cleaned_path = DATA_DIR / "cleaned_600519_SS_2024.csv"
    df.to_csv(cleaned_path, index=False, encoding="utf-8-sig")
    return cleaned_path


def save_data_preview(df: pd.DataFrame) -> None:
    preview_path = OUTPUT_DIR / "data_preview.txt"
    with preview_path.open("w", encoding="utf-8") as fh:
        fh.write("Top 5 rows of cleaned data\n")
        fh.write(df.head().to_string(index=False))
        fh.write("\n\nData types\n")
        fh.write(df.dtypes.to_string())


def save_table_image(df: pd.DataFrame, path: Path, title: str) -> Path:
    fig, ax = plt.subplots(figsize=(14, 3.8))
    ax.axis("off")
    tbl = ax.table(
        cellText=df.values,
        colLabels=df.columns,
        loc="center",
        cellLoc="center",
    )
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(9)
    tbl.scale(1, 1.5)
    plt.title(title, pad=12)
    plt.tight_layout()
    plt.savefig(path, dpi=200, bbox_inches="tight")
    plt.close()
    return path


def plot_close_price(df: pd.DataFrame) -> Path:
    plt.figure(figsize=(12, 6))
    sns.lineplot(data=df, x="Date", y="Close", linewidth=1.8, color="#2563eb")
    plt.title("600519.SS Close Price Trend (2024)")
    plt.xlabel("Date")
    plt.ylabel("Close Price")
    plt.grid(alpha=0.3)
    plt.tight_layout()
    out = OUTPUT_DIR / "close_price.png"
    plt.savefig(out, dpi=200)
    plt.close()
    return out


def plot_sma(df: pd.DataFrame) -> Path:
    plt.figure(figsize=(12, 6))
    sns.lineplot(data=df, x="Date", y="Close", label="Close", linewidth=1.6, color="#1d4ed8")
    sns.lineplot(data=df, x="Date", y="SMA_20", label="SMA 20", linewidth=1.6, color="#f97316")
    sns.lineplot(data=df, x="Date", y="SMA_50", label="SMA 50", linewidth=1.6, color="#16a34a")
    plt.title("600519.SS Close Price with Moving Averages")
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.grid(alpha=0.3)
    plt.legend()
    plt.tight_layout()
    out = OUTPUT_DIR / "sma.png"
    plt.savefig(out, dpi=200)
    plt.close()
    return out


def plot_rsi(df: pd.DataFrame) -> Path:
    plt.figure(figsize=(12, 6))
    sns.lineplot(data=df, x="Date", y="RSI_14", linewidth=1.6, color="#2563eb")
    plt.axhline(70, color="#dc2626", linestyle="--", label="Overbought 70")
    plt.axhline(30, color="#16a34a", linestyle="--", label="Oversold 30")
    plt.title("600519.SS RSI(14)")
    plt.xlabel("Date")
    plt.ylabel("RSI")
    plt.ylim(0, 100)
    plt.grid(alpha=0.3)
    plt.legend()
    plt.tight_layout()
    out = OUTPUT_DIR / "rsi.png"
    plt.savefig(out, dpi=200)
    plt.close()
    return out


def plot_cumulative_return(df: pd.DataFrame) -> Path:
    plt.figure(figsize=(12, 6))
    sns.lineplot(data=df, x="Date", y="Cumulative_Return", linewidth=1.8, color="#7c3aed")
    plt.title("600519.SS Cumulative Return (2024)")
    plt.xlabel("Date")
    plt.ylabel("Cumulative Return")
    plt.grid(alpha=0.3)
    plt.tight_layout()
    out = OUTPUT_DIR / "cumulative_return.png"
    plt.savefig(out, dpi=200)
    plt.close()
    return out


def summarize(df: pd.DataFrame, missing_before: pd.Series, missing_after: pd.Series) -> dict:
    latest = df.iloc[-1]
    first_close = float(df["Close"].iloc[0])
    last_close = float(df["Close"].iloc[-1])
    total_return = (last_close / first_close) - 1
    daily_volatility = float(df["Daily_Return"].std())
    annualized_volatility = daily_volatility * (252 ** 0.5)
    latest_rsi = float(df["RSI_14"].dropna().iloc[-1])

    return {
        "ticker": TICKER,
        "start_date": START_DATE,
        "end_date": END_DATE,
        "row_count": int(len(df)),
        "first_close": round(first_close, 2),
        "last_close": round(last_close, 2),
        "total_return": round(total_return * 100, 2),
        "daily_volatility": round(daily_volatility * 100, 2),
        "annualized_volatility": round(annualized_volatility * 100, 2),
        "latest_rsi": round(latest_rsi, 2),
        "latest_sma_20": round(float(latest["SMA_20"]), 2),
        "latest_sma_50": round(float(latest["SMA_50"]), 2),
        "missing_before": {k: int(v) for k, v in missing_before.items()},
        "missing_after": {k: int(v) for k, v in missing_after.items()},
    }


def save_summary(summary: dict) -> tuple[Path, Path]:
    text_path = OUTPUT_DIR / "analysis_summary.txt"
    json_path = OUTPUT_DIR / "analysis_summary.json"

    interpretation = [
        f"Ticker: {summary['ticker']}",
        f"Date range: {summary['start_date']} to {summary['end_date']}",
        f"Trading rows: {summary['row_count']}",
        f"First close price: {summary['first_close']}",
        f"Last close price: {summary['last_close']}",
        f"Total return: {summary['total_return']}%",
        f"Daily volatility: {summary['daily_volatility']}%",
        f"Annualized volatility: {summary['annualized_volatility']}%",
        f"Latest RSI(14): {summary['latest_rsi']}",
        f"Latest SMA20: {summary['latest_sma_20']}",
        f"Latest SMA50: {summary['latest_sma_50']}",
        "",
        "Missing values before fill:",
        json.dumps(summary["missing_before"], ensure_ascii=False, indent=2),
        "",
        "Missing values after fill:",
        json.dumps(summary["missing_after"], ensure_ascii=False, indent=2),
    ]

    text_path.write_text("\n".join(interpretation), encoding="utf-8")
    json_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return text_path, json_path


def main() -> None:
    ensure_dirs()
    sns.set_theme(style="whitegrid")

    raw_df = fetch_data()
    if raw_df.empty:
        raise RuntimeError("No data was returned from Yahoo Finance.")
    raw_path = save_raw_data(raw_df)

    clean_df, missing_before, missing_after = clean_data(raw_df)
    analysis_df = add_indicators(clean_df)
    cleaned_path = save_cleaned_data(analysis_df)
    save_data_preview(analysis_df)
    save_table_image(
        analysis_df.head().round(2),
        OUTPUT_DIR / "data_preview.png",
        "Top 5 Rows of Cleaned Data",
    )
    missing_df = pd.DataFrame(
        {
            "Column": list(missing_before.index),
            "Missing Before": list(missing_before.values),
            "Missing After": [missing_after.get(col, 0) for col in missing_before.index],
        }
    )
    save_table_image(
        missing_df,
        OUTPUT_DIR / "missing_values.png",
        "Missing Value Check",
    )

    close_chart = plot_close_price(analysis_df)
    sma_chart = plot_sma(analysis_df)
    rsi_chart = plot_rsi(analysis_df)
    cumret_chart = plot_cumulative_return(analysis_df)

    summary = summarize(analysis_df, missing_before, missing_after)
    summary_txt, summary_json = save_summary(summary)

    print("Analysis completed.")
    print(f"Raw data: {raw_path}")
    print(f"Cleaned data: {cleaned_path}")
    print(f"Close chart: {close_chart}")
    print(f"SMA chart: {sma_chart}")
    print(f"RSI chart: {rsi_chart}")
    print(f"Cumulative return chart: {cumret_chart}")
    print(f"Summary text: {summary_txt}")
    print(f"Summary json: {summary_json}")
    print(
        f"Key metrics: total_return={summary['total_return']}%, "
        f"daily_volatility={summary['daily_volatility']}%, "
        f"latest_rsi={summary['latest_rsi']}"
    )


if __name__ == "__main__":
    main()
