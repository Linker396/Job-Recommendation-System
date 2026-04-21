"""数据清洗与去重模块"""
import hashlib
import re
from typing import List, Dict, Any


class JobProcessor:
    """对原始岗位数据进行去重"""

    def __init__(self, max_records: int = 0):
        """
        Args:
            max_records: 最大保留记录数，0 表示不限制
        """
        self.seen: set = set()
        self.max_records = max_records

    def _dedup_key(self, job: Dict[str, Any]) -> str:
        """基于 jobName + companyName 生成去重键"""
        title = re.sub(r"\s+", "", job.get("jobName", "")).lower()
        company = re.sub(r"\s+", "", job.get("companyName", "")).lower()
        return hashlib.md5(f"{title}|{company}".encode()).hexdigest()

    def process(self, jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """去重"""
        cleaned = []
        for job in jobs:
            if not job.get("jobName") or not job.get("companyName"):
                continue

            key = self._dedup_key(job)
            if key in self.seen:
                continue
            self.seen.add(key)

            if self.max_records and len(cleaned) >= self.max_records:
                break

            cleaned.append(job)
        return cleaned
