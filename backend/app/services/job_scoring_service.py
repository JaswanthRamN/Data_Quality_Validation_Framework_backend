"""
Multi-factor job scoring service — combines ATS analysis with contextual signals
to produce a composite 0-100 score for ranking.
"""

import logging
from typing import Optional
from app.config import settings
from app.models.job import Job

logger = logging.getLogger(__name__)


class JobScoringService:
    """
    Computes a weighted composite score (0-100) for each job based on:
    - ATS match score (30%)
    - Sponsorship likelihood (20%)
    - Remote/hybrid flexibility (15%)
    - Salary potential (15%)
    - Skills overlap (10%)
    - Company reputation signal (5%)
    - Career growth signal (5%)
    """

    def __init__(self):
        self.w_ats = settings.SCORE_WEIGHT_ATS
        self.w_sponsorship = settings.SCORE_WEIGHT_SPONSORSHIP
        self.w_remote = settings.SCORE_WEIGHT_REMOTE
        self.w_salary = settings.SCORE_WEIGHT_SALARY
        self.w_skills = settings.SCORE_WEIGHT_SKILLS
        self.w_company = settings.SCORE_WEIGHT_COMPANY
        self.w_growth = settings.SCORE_WEIGHT_GROWTH

        self.salary_min = settings.SALARY_SCORE_MIN
        self.salary_max = settings.SALARY_SCORE_MAX

    # ── Individual factor scorers ─────────────────────────────────────────────

    def _score_ats(self, ats_score: Optional[float]) -> float:
        """Direct 0-100 pass-through."""
        return float(ats_score) if ats_score is not None else 50.0

    def _score_sponsorship(self, sponsorship_likely: bool, description: str) -> float:
        """100 if likely, 50 if unknown, 20 if description implies no sponsorship."""
        if sponsorship_likely:
            return 100.0
        desc_lower = (description or "").lower()
        no_sponsor_signals = ["no sponsorship", "not sponsor", "citizens only", "permanent resident"]
        if any(s in desc_lower for s in no_sponsor_signals):
            return 20.0
        return 50.0  # unknown

    def _score_remote(self, is_remote: bool, is_hybrid: bool) -> float:
        if is_remote:
            return 100.0
        if is_hybrid:
            return 60.0
        return 20.0  # onsite only

    def _score_salary(self, salary_min: Optional[float], salary_max: Optional[float]) -> float:
        if salary_max is None and salary_min is None:
            return 50.0  # unknown salary, neutral
        value = salary_max or salary_min or 0
        if value <= self.salary_min:
            return 10.0
        if value >= self.salary_max:
            return 100.0
        return round((value - self.salary_min) / (self.salary_max - self.salary_min) * 100, 1)

    def _score_skills(self, skill_match_pct: Optional[float]) -> float:
        return float(skill_match_pct) if skill_match_pct is not None else 50.0

    def _score_company(self, company: str, description: str) -> float:
        """Simple heuristic: fast-growing/AI/tech companies score higher."""
        combined = f"{company} {description}".lower()
        signals = [
            ("series", 15), ("funded", 10), ("ai", 10), ("machine learning", 10),
            ("saas", 8), ("platform", 5), ("startup", 5), ("scale", 5),
            ("fortune 500", 5), ("inc 5000", 8),
        ]
        score = 50.0
        for keyword, bonus in signals:
            if keyword in combined:
                score = min(100.0, score + bonus)
        return score

    def _score_growth(self, title: str, description: str) -> float:
        """Heuristic for career growth potential based on role and description."""
        combined = f"{title} {description}".lower()
        growth_signals = [
            ("senior", 20), ("lead", 15), ("manager", 10), ("principal", 20),
            ("staff", 15), ("architect", 20), ("director", 10),
            ("growth", 8), ("learning", 5), ("mentorship", 10),
        ]
        score = 50.0
        for keyword, bonus in growth_signals:
            if keyword in combined:
                score = min(100.0, score + bonus)
                break  # only count the highest seniority signal
        return score

    # ── Composite scorer ──────────────────────────────────────────────────────

    def score_job(self, job: Job, analysis: dict) -> float:
        """Compute weighted composite score 0-100."""
        ats_s = self._score_ats(analysis.get("ats_score"))
        sponsor_s = self._score_sponsorship(job.sponsorship_likely, job.description or "")
        remote_s = self._score_remote(job.is_remote, job.is_hybrid)
        salary_s = self._score_salary(job.salary_min, job.salary_max)
        skills_s = self._score_skills(analysis.get("skill_match_pct"))
        company_s = self._score_company(job.company, job.description or "")
        growth_s = self._score_growth(job.title, job.description or "")

        composite = (
            ats_s * self.w_ats
            + sponsor_s * self.w_sponsorship
            + remote_s * self.w_remote
            + salary_s * self.w_salary
            + skills_s * self.w_skills
            + company_s * self.w_company
            + growth_s * self.w_growth
        )
        return round(composite, 2)

    def rank_jobs(self, scored_jobs: list[tuple[Job, float]]) -> list[tuple[Job, float]]:
        """Return jobs sorted by composite score descending."""
        return sorted(scored_jobs, key=lambda x: x[1], reverse=True)
