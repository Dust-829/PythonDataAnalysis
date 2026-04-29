# 数据说明文档

## Demo 数据说明

- 本数据仅用于无网络环境下验证代码流程，不用于最终课程提交。
- 生成时间：2026-04-29T11:04:18+08:00
- 评分记录数：30000
- 电影数量：1200
- 用户数量：900

## 最终处理数据字段

- `ratings_final.csv`：评分级最终数据，用于统计分析、回归、分类和展示。
- `movies_final.csv`：电影级汇总数据，用于聚类和电影维度分析。
- 关键字段包括：userId、movieId、rating、rating_datetime、rating_year、rating_month、title、genres、primary_genre、genre_count、release_year、release_age、movie_rating_mean、movie_rating_count、user_rating_mean、user_rating_count、averageRating、numVotes、tag_count、tag_unique_count、各 genre_* 编码字段等。
- 清洗报告：{'ratings_rows_raw': 30000, 'movies_rows_raw': 1200, 'links_rows_raw': 1200, 'tags_rows_raw': 2400, 'ratings_rows_after_sampling': 30000, 'duplicate_rating_rows_removed': 0, 'rating_outlier_rows': 0, 'final_rating_rows': 30000, 'final_rating_columns': 46, 'final_movie_rows': 1200, 'final_movie_columns': 34, 'top_missing_columns': {'runtimeMinutes': 30000, 'userId': 0, 'rating': 0, 'timestamp': 0, 'rating_datetime': 0, 'movieId': 0, 'rating_month': 0, 'is_high_rating': 0, 'user_rating_count': 0, 'user_rating_mean': 0, 'title': 0, 'genres': 0, 'title_year': 0, 'rating_year': 0, 'clean_title': 0, 'genre_count': 0, 'genre_Adventure': 0, 'genre_Action': 0, 'genre_Comedy': 0, 'genre_Crime': 0}}
