from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import streamlit as st


ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
FIGURES = ROOT / "output" / "figures"
METRICS = ROOT / "output" / "metrics"


st.set_page_config(page_title="电影评分与受欢迎度分析", layout="wide")
st.title("电影评分与受欢迎度分析")


@st.cache_data
def load_data() -> pd.DataFrame:
    path = PROCESSED / "ratings_final.csv"
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path, low_memory=False)


df = load_data()
if df.empty:
    st.warning("未找到处理后的数据。请先运行 src/collect_movielens.py、src/collect_imdb.py 和 src/clean_merge.py。")
    st.stop()

st.metric("评分记录数", f"{len(df):,}")
st.metric("字段数量", f"{df.shape[1]:,}")

tab_overview, tab_charts, tab_models, tab_conclusion = st.tabs(["数据概览", "可视化", "模型结果", "结论"])

with tab_overview:
    cols = st.columns(4)
    cols[0].metric("电影数量", f"{df['movieId'].nunique():,}")
    cols[1].metric("用户数量", f"{df['userId'].nunique():,}")
    cols[2].metric("平均评分", f"{df['rating'].mean():.2f}")
    cols[3].metric("高分比例", f"{df['is_high_rating'].mean():.1%}")
    st.dataframe(df.head(200), use_container_width=True)

with tab_charts:
    st.subheader("热门电影类型")
    st.bar_chart(df["primary_genre"].value_counts().head(15))

    st.subheader("年度平均评分趋势")
    yearly = df.groupby("rating_year")["rating"].mean().sort_index()
    st.line_chart(yearly)

    st.subheader("上映年份与评分关系")
    scatter_df = df.sample(min(len(df), 5000), random_state=42)[["release_year", "rating"]].dropna()
    st.scatter_chart(scatter_df, x="release_year", y="rating")
    for image_name in ["heatmap_correlation.png", "wordcloud_tags.png", "cluster_kmeans.png"]:
        image_path = FIGURES / image_name
        if image_path.exists():
            st.image(str(image_path), caption=image_name)

with tab_models:
    for metric_file in ["regression_metrics.json", "classification_metrics.json", "clustering_metrics.json"]:
        path = METRICS / metric_file
        if path.exists():
            st.subheader(metric_file)
            st.json(json.loads(path.read_text(encoding="utf-8")))
    for image_name in ["regression_predictions.png", "classification_roc_curves.png", "cluster_kmeans.png", "cluster_agglomerative.png"]:
        image_path = FIGURES / image_name
        if image_path.exists():
            st.image(str(image_path), caption=image_name)

with tab_conclusion:
    st.write("本页面用于集中展示电影评分数据的统计分析、可视化结果和模型评价。")
    st.write("最终结论应结合实际运行后的图表和指标，在实验报告中进一步展开，包括热门类型、评分趋势、影响评分的因素、高分电影特征和聚类画像。")
