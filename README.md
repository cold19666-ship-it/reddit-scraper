# Reddit Scraper

手动触发的 Reddit 数据抓取工具，数据存储在 `data/` 目录。

## 使用方式

GitHub 仓库页面 → Actions → Reddit Scraper → Run workflow

## 数据格式

每次运行在 `data/` 目录生成或追加 `{subreddit}_{日期}.json`，字段包括：
`id / title / score / url / permalink / num_comments / created_utc / author / selftext`

## 修改配置

编辑 `scraper.py` 第一行：
- 换 subreddit：`SUBREDDITS = ["MachineLearning"]`
- 多个 subreddit：`SUBREDDITS = ["MachineLearning", "artificial"]`
- 抓取数量：`LIMIT = 25`
