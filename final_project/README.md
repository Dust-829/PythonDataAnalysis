# Python 数据分析期末大作业

## 项目主题

电影评分与受欢迎度分析。

本项目用于完成《Python 数据分析》课程期末大作业。项目将使用公开电影数据集，完成数据采集、数据清洗、统计分析、数据可视化、回归模型、分类模型、聚类模型、Streamlit 可视化展示页面和最终实验报告。

## 当前计划

项目计划使用 MovieLens 作为用户评分和标签数据来源，使用 IMDb 非商业数据集作为电影元数据和外部评分数据来源。两个数据源通过 MovieLens `links.csv` 中的 IMDb ID 与 IMDb `tconst` 字段进行关联。

最终处理后的数据集需要满足以下硬性要求：

- 数据记录数不少于 20,000 条。
- 有效字段不少于 20 项。
- 数据来源不少于 2 个采集脚本。
- 数据说明文档需要记录字段含义、数据单位、采集时间和数据范围。

## 当前实现状态

- 已完成项目目录、依赖文件、数据采集脚本、清洗合并脚本、EDA 可视化脚本、回归/分类/聚类模型脚本、Streamlit 展示页和报告生成脚本。
- 当前环境的网络权限阻止直接下载 MovieLens/IMDb 数据，真实数据采集脚本已经写好，但尚未完成真实数据下载。
- 为验证流程，已使用 `src/generate_demo_data.py` 生成 demo 数据并完成烟测；demo 数据仅用于本地流程验证，不能用于最终课程提交。
- demo 烟测结果：`ratings_final.csv` 生成 30,000 条记录、46 个字段，满足结构上的 20,000+ 记录和 20+ 字段要求。
- 已生成 EDA 图表、统计表、回归指标、分类指标、聚类指标和 `report/final_experiment_report.docx`。
- DOCX 可生成，但当前沙箱权限阻止 LibreOffice 渲染检查；后续正式报告完成后需要在本机 Word/WPS 或可用渲染环境中检查版面。

## 计划交付物

- 至少 2 个数据采集脚本。
- 原始数据、中间数据和最终处理数据。
- 数据说明文档。
- 数据清洗过程记录和清洗前后数据量对比。
- 统计分析表格和可视化图表。
- 回归、分类、聚类模型结果和评价指标。
- Streamlit 数据分析展示页面。
- 最终 DOCX 实验报告。
- 用于提交的项目工程压缩包。

## 计划目录结构

```text
final_project/
+-- AGENTS.md
+-- README.md
+-- requirements.txt
+-- data/
|   +-- raw/
|   +-- interim/
|   +-- processed/
|   +-- data_dictionary.md
+-- src/
|   +-- collect_movielens.py
|   +-- collect_imdb.py
|   +-- clean_merge.py
|   +-- eda_visualize.py
|   +-- model_regression.py
|   +-- model_classification.py
|   +-- model_clustering.py
|   +-- build_report_assets.py
+-- notebooks/
+-- output/
|   +-- figures/
|   +-- tables/
|   +-- metrics/
+-- app/
|   +-- streamlit_app.py
+-- report/
    +-- final_experiment_report.docx
```

## 计划执行流程

1. 从 MovieLens 和 IMDb 采集电影评分、标签和元数据。
2. 记录数据来源 URL、采集时间、行数、文件大小、字段含义和数据范围。
3. 通过 IMDb ID 合并 MovieLens 和 IMDb 数据集。
4. 处理缺失值、重复值、异常值、数据类型错误、格式错误和逻辑错误。
5. 构建建模特征，包括时间字段、类型字段、标签字段和类别编码字段。
6. 生成描述性统计、透视表、分组汇总和相关性分析结果。
7. 生成必需图表，包括缺失值热力图、折线图、柱状图、饼图、散点图、箱线图、直方图、相关性热力图、时序图、QQ 图和词云。
8. 训练并评价至少 2 个回归模型、4 个分类模型和 2 个聚类模型。
9. 构建 Streamlit 展示页面，展示核心图表、模型指标和实践结论。
10. 使用生成的表格、图表和展示页结果撰写最终实验报告。

## 运行命令

在 `final_project` 目录下执行：

```powershell
pip install -r requirements.txt
python src/collect_movielens.py --size small
python src/collect_imdb.py
python src/clean_merge.py
python src/eda_visualize.py
python src/model_regression.py
python src/model_classification.py
python src/model_clustering.py
python src/build_report_assets.py
streamlit run app/streamlit_app.py
```

说明：`collect_movielens.py` 默认建议先使用 `--size small`，可以满足 20,000+ 记录要求且运行速度较快；如果后续需要更大规模数据，可改为 `--size full`。IMDb 文件较大，下载时间取决于网络环境。展示页使用 Streamlit 自带图表，减少额外依赖。

如果当前网络无法下载真实数据，可以先运行下面的命令生成 demo 数据进行流程烟测。注意：demo 数据只能用于本地验证代码流程，不能作为最终课程提交数据。

```powershell
python src/generate_demo_data.py
python src/clean_merge.py
python src/eda_visualize.py
python src/model_regression.py
python src/model_classification.py
python src/model_clustering.py
```

最终打包时建议使用：

```powershell
python src/make_submission_zip.py --output submission_project.zip
```

该脚本会自动排除 `__pycache__`、临时目录和 demo 数据，避免把无关缓存文件提交上去。

## 评分点对照

- 数据采集：2 个以上采集脚本、数据持久化保存、数据说明文档。
- 数据清洗：缺失值、重复值、异常值、数据标准化、数据合并、特征处理。
- 统计分析：均值、中位数、方差、标准差、分位数、频数和频率。
- 数据可视化：基础图表和分析型图表。
- 综合分析：分组分析、透视表、交叉分析、相关性分析、时序分析、分布分析、归因分析和业务洞察。
- 回归模型：至少 2 个回归模型，并输出 MAE、MSE、R2 等评价指标。
- 分类模型：至少 4 个分类模型，并输出准确率、精确率、召回率、F1、ROC、AUC 和混淆矩阵。
- 聚类模型：至少 2 个聚类模型，并可视化聚类结果、解释各类特征。
- 创新点：Streamlit 展示页面、额外分析方法、实践指导价值结论。
- 实验报告：内容完整、分析准确、格式正确、提交文件齐全。

## 执行说明

本 README 是项目的滚动计划和对外说明文档。后续实现过程中，如果实际数据源、目录结构、脚本名称、模型选择、输出文件或报告状态发生变化，需要同步更新本文档。
