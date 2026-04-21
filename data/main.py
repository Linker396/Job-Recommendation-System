"""
岗位数据爬虫入口脚本（自动模式）

支持自动检测滑动验证码（可见模式）：
  - 检测到验证码时暂停，等待用户在浏览器窗口手动滑动
  - 滑动完成后自动继续抓取

输出三个文件：
  - jobs_raw.json     原始数据（含 sensorsdata JSON 和详情链接）
  - jobs_cleaned.json 清洗后数据（统一字段格式）
  - jobs.json          最终去重数据（最多 200 条）
"""
import json
import sys
import time
from loguru import logger

logger.remove()
logger.add(
    sys.stderr,
    format="{time:HH:mm:ss} | {level} | {message}",
    level="INFO",
    colorize=False,
)

from crawler import JobsdbCrawler
from processor import JobProcessor
from config import KEYWORDS, CITIES_51JOB, PAGE_SIZE, MAX_PAGES, MAX_RECORDS


def main():
    start = time.time()
    logger.info("=" * 50)
    logger.info("开始抓取 AI 相关岗位...")
    logger.info(f"关键词={KEYWORDS}，目标至少 {MAX_RECORDS} 条")
    logger.info("可见模式：检测到验证码时需在浏览器窗口手动滑动")
    logger.info("=" * 50)

    crawler = JobsdbCrawler(headless=False)

    raw_all = []      # 原始数据
    cleaned_all = []   # 清洗后数据

    page_total = 0
    raw_total = 0

    for keyword in KEYWORDS:
        for _city_name, city_code in CITIES_51JOB:
            if len(cleaned_all) >= MAX_RECORDS:
                break

            for page in range(1, MAX_PAGES + 1):
                if len(cleaned_all) >= MAX_RECORDS:
                    break

                raw_jobs = crawler.fetch_jobs(keyword, city_code, page, PAGE_SIZE)
                page_total += 1
                raw_total += len(raw_jobs)

                for raw in raw_jobs:
                    if not raw.get("jobName"):
                        continue
                    # 原始数据：保存 sensorsdata 和详情链接
                    raw_all.append({
                        "sensorsdata": raw.get("_sensorsdata", {}),
                        "detail_link": raw.get("_detail_link", ""),
                    })
                    # 清洗后数据
                    job = crawler.parse_job(raw)
                    if job.get("jobName"):
                        cleaned_all.append(job)

                logger.info(f"当前累计 {len(cleaned_all)} 条清洗后数据")

            if len(cleaned_all) >= MAX_RECORDS:
                break

    crawler.close()

    # ========== 输出三个文件 ==========
    processor = JobProcessor()

    # 1. 原始数据
    with open("jobs_raw.json", "w", encoding="utf-8") as f:
        json.dump(raw_all, f, ensure_ascii=False, indent=2)
    logger.info(f"[1/3] 原始数据已保存: jobs_raw.json ({len(raw_all)} 条)")

    # 2. 清洗后数据
    with open("jobs_cleaned.json", "w", encoding="utf-8") as f:
        json.dump(cleaned_all, f, ensure_ascii=False, indent=2)
    logger.info(f"[2/3] 清洗后数据已保存: jobs_cleaned.json ({len(cleaned_all)} 条)")

    # 3. 去重数据
    final_jobs = processor.process(cleaned_all)
    final_jobs = final_jobs[:MAX_RECORDS]

    with open("jobs.json", "w", encoding="utf-8") as f:
        json.dump(final_jobs, f, ensure_ascii=False, indent=2)

    has_desc = sum(1 for j in final_jobs if j.get("jobDescribe"))
    elapsed = time.time() - start
    logger.success(
        f"[3/3] 完成！共 {len(final_jobs)} 条（含 {has_desc} 条完整描述），"
        f"耗时 {elapsed:.1f}s"
    )


if __name__ == "__main__":
    main()
