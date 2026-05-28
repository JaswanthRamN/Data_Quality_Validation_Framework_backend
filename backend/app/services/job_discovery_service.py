"""
Job discovery service — wraps the Indeed MCP tool and normalizes job data.
"""

import logging
import hashlib
import re
from typing import List, Dict, Optional
from datetime import datetime

from app.config import settings
from app.schemas.job_schema import JobCreate

logger = logging.getLogger(__name__)

USER_CORE_SKILLS = [
    "sql", "python", "pandas", "numpy", "power bi", "tableau", "excel",
    "dbt", "airflow", "snowflake", "redshift", "postgresql", "mysql",
    "aws", "s3", "lambda", "spark", "pyspark", "databricks",
    "salesforce", "sap", "netsuite", "erp", "etl", "elt",
    "scikit-learn", "machine learning", "regression", "a/b testing",
    "time series", "forecasting", "data modeling", "data warehousing",
    "looker", "metabase", "google analytics", "bigquery", "azure",
    "r", "statistics", "data visualization", "dashboard",
]

# Canonical role category mapping from job title keywords
ROLE_CATEGORY_MAP = {
    "analytics engineer": "Analytics Engineer",
    "data engineer": "Analytics Engineer",
    "business intelligence": "Business Intelligence Analyst",
    "bi analyst": "Business Intelligence Analyst",
    "bi developer": "Business Intelligence Analyst",
    "product analyst": "Product Analyst",
    "reporting analyst": "Reporting Analyst",
    "revenue operations": "Revenue Operations Analyst",
    "revops": "Revenue Operations Analyst",
    "supply chain": "Supply Chain Analyst",
    "procurement analyst": "Procurement Analyst",
    "logistics analyst": "Logistics Analyst",
    "operations analyst": "Operations Analyst",
    "business analyst": "Business Analyst",
    "data analyst": "Data Analyst",
}


def _categorize_role(title: str) -> str:
    """Map a raw job title to a canonical role category."""
    title_lower = title.lower()
    for keyword, category in ROLE_CATEGORY_MAP.items():
        if keyword in title_lower:
            return category
    return "Data Analyst"  # default


def _make_external_id(source: str, title: str, company: str, location: str) -> str:
    """Generate a stable dedup key when the platform doesn't provide one."""
    raw = f"{source}:{title.lower()}:{company.lower()}:{(location or '').lower()}"
    return hashlib.md5(raw.encode()).hexdigest()


def _is_excluded(title: str, description: str) -> bool:
    """Return True if the job should be filtered out."""
    combined = f"{title} {description}".lower()
    return any(kw.lower() in combined for kw in settings.JOB_EXCLUSION_KEYWORDS)


def _detect_sponsorship(title: str, description: str, company: str) -> bool:
    """Return True if the listing suggests visa sponsorship is possible."""
    combined = f"{title} {description} {company}".lower()
    return any(kw.lower() in combined for kw in settings.JOB_SPONSORSHIP_KEYWORDS)


def _detect_remote(title: str, location: str, description: str) -> tuple[bool, bool]:
    """Return (is_remote, is_hybrid) flags."""
    combined = f"{title} {location} {description}".lower()
    is_remote = "remote" in combined and "hybrid" not in combined
    is_hybrid = "hybrid" in combined
    return is_remote, is_hybrid


def _parse_salary(salary_str: str) -> tuple[Optional[float], Optional[float]]:
    """Extract min/max salary from a string like '$95,000 - $120,000 a year'."""
    if not salary_str:
        return None, None
    nums = re.findall(r"[\d,]+", salary_str.replace(",", ""))
    # Filter out obviously wrong values (hourly rates parsed as annual)
    values = [float(n) for n in nums if 20000 <= float(n) <= 500000]
    if len(values) >= 2:
        return min(values), max(values)
    if len(values) == 1:
        return values[0], values[0]
    return None, None


def normalize_indeed_job(raw: dict, location_search: str) -> Optional[JobCreate]:
    """
    Convert a raw Indeed MCP job result dict into a JobCreate schema.
    Returns None if the job should be excluded.
    """
    title = raw.get("title", "")
    company = raw.get("company", "")
    location = raw.get("location", location_search)
    description = raw.get("description", "") or raw.get("snippet", "")
    apply_url = raw.get("applyLink") or raw.get("link") or raw.get("url", "")
    external_id = raw.get("jobId") or raw.get("id") or _make_external_id(
        "indeed", title, company, location
    )
    salary_str = raw.get("salary", "") or ""

    if _is_excluded(title, description):
        logger.debug(f"Excluded job: {title} @ {company}")
        return None

    salary_min, salary_max = _parse_salary(salary_str)
    is_remote, is_hybrid = _detect_remote(title, location, description)

    return JobCreate(
        source="indeed",
        external_id=str(external_id),
        title=title,
        company=company,
        location=location,
        is_remote=is_remote,
        is_hybrid=is_hybrid,
        salary_min=salary_min,
        salary_max=salary_max,
        description=description,
        apply_url=apply_url,
        posted_date=None,
        role_category=_categorize_role(title),
        sponsorship_likely=_detect_sponsorship(title, description, company),
        is_excluded=False,
    )


def parse_indeed_search_results(markdown_text: str, location: str) -> List[dict]:
    """
    Parse job listings from the Indeed MCP markdown response.
    The MCP returns formatted markdown — we extract structured fields.
    Each job block typically looks like:
      ## Job Title
      **Company** | Location | Salary
      Description snippet...
      [Apply](url)
    """
    jobs = []
    # Split on markdown job headings
    blocks = re.split(r"\n(?=#{1,3} )", markdown_text.strip())
    for block in blocks:
        if not block.strip():
            continue

        lines = block.strip().split("\n")
        title_line = lines[0].lstrip("#").strip()

        # Extract apply link
        apply_match = re.search(r"\[(?:Apply|apply)[^\]]*\]\(([^)]+)\)", block)
        apply_url = apply_match.group(1) if apply_match else ""

        # Extract job ID from URL query params
        job_id_match = re.search(r"jk=([a-z0-9]+)", apply_url)
        job_id = job_id_match.group(1) if job_id_match else ""

        # Handle "**Company:** Name **Location:** Place" style metadata
        company_kv = re.search(r"\*\*Company:?\*\*\s*([^\n*|]+)", block, re.IGNORECASE)
        location_kv = re.search(r"\*\*Location:?\*\*\s*([^\n*|]+)", block, re.IGNORECASE)
        if company_kv:
            company = company_kv.group(1).strip().rstrip("*").strip()
            location_found = location_kv.group(1).strip().rstrip("*").strip() if location_kv else location
        else:
            # Fallback: plain "**Company** | Location" style
            meta_match = re.search(r"\*\*([^*:]+)\*\*\s*\|?\s*([^|\n]+)?", block)
            company = meta_match.group(1).strip() if meta_match else "Unknown"
            location_found = meta_match.group(2).strip() if meta_match and meta_match.group(2) else location

        # Extract salary if present
        salary_match = re.search(r"\$[\d,]+(?:\s*[-–]\s*\$[\d,]+)?(?:\s*(?:a year|/yr|/year|annually))?", block)
        salary = salary_match.group(0) if salary_match else ""

        # Rest is description
        description_parts = []
        for line in lines[1:]:
            clean = line.strip().lstrip("*").rstrip("*").strip()
            if clean and not clean.startswith("[Apply") and not clean.startswith("**"):
                description_parts.append(clean)
        description = " ".join(description_parts[:5])

        jobs.append({
            "jobId": job_id or _make_external_id("indeed", title_line, company, location_found),
            "title": title_line,
            "company": company,
            "location": location_found,
            "salary": salary,
            "description": description,
            "applyLink": apply_url,
        })

    return jobs


class JobDiscoveryService:
    """
    Orchestrates multi-role, multi-location job searches using the Indeed MCP tool.
    Call search_all_roles() from a Celery task or API endpoint.
    """

    def __init__(self):
        self.target_roles = settings.JOB_TARGET_ROLES
        self.target_locations = settings.JOB_TARGET_LOCATIONS

    def build_search_queries(self) -> List[tuple[str, str]]:
        """Returns (role, location) pairs to search."""
        queries = []
        for role in self.target_roles:
            for location in self.target_locations:
                queries.append((role, location))
        return queries

    def process_search_results(
        self, raw_markdown: str, role: str, location: str
    ) -> List[JobCreate]:
        """
        Parse the Indeed MCP markdown response and return normalized JobCreate objects.
        This is called with the MCP tool output from the Celery task / route handler
        because MCP tools are only callable from the main Claude context, not from
        within Python service code.
        """
        raw_jobs = parse_indeed_search_results(raw_markdown, location)
        results: List[JobCreate] = []
        seen_ids = set()

        for raw in raw_jobs:
            job = normalize_indeed_job(raw, location)
            if job is None:
                continue
            if job.external_id in seen_ids:
                continue
            seen_ids.add(job.external_id)
            results.append(job)

        logger.info(
            f"Processed {len(results)} valid jobs for '{role}' in '{location}' "
            f"(skipped {len(raw_jobs) - len(results)})"
        )
        return results

    def deduplicate(self, jobs: List[JobCreate]) -> List[JobCreate]:
        """Cross-query deduplication by (company, title, location)."""
        seen = set()
        unique = []
        for job in jobs:
            key = f"{job.company.lower()}|{job.title.lower()}|{(job.location or '').lower()}"
            if key not in seen:
                seen.add(key)
                unique.append(job)
        return unique
