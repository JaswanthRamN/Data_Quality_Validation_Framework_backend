"""
ATS analysis service — uses Claude claude-sonnet-4-6 when API key is available,
falls back to TF-IDF keyword matching otherwise.
"""

import json
import logging
import re
import time
from typing import Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

from app.config import settings

logger = logging.getLogger(__name__)

# Skills to track for the user's background
USER_CORE_SKILLS = [
    "sql", "python", "tableau", "power bi", "etl", "pipeline", "snowflake",
    "aws", "salesforce", "erp", "dashboard", "kpi", "forecasting",
    "data validation", "analytics", "reporting", "visualization",
    "excel", "dbt", "airflow", "spark", "looker", "data warehouse",
]


# ── Fallback analyzer (no API key) ───────────────────────────────────────────

class FallbackATSAnalyzer:
    """
    TF-IDF keyword-based ATS scoring used when ANTHROPIC_API_KEY is not set.
    Provides ats_score, skill_match_pct, missing_keywords — no generated content.
    """

    def analyze(self, resume_text: str, job_description: str) -> dict:
        resume_lower = resume_text.lower()
        jd_lower = job_description.lower()

        # Extract keywords from JD using TF-IDF
        try:
            vectorizer = TfidfVectorizer(
                stop_words="english", ngram_range=(1, 2), max_features=50
            )
            tfidf_matrix = vectorizer.fit_transform([jd_lower, resume_lower])
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            ats_score = round(float(similarity) * 100, 1)
            keywords = vectorizer.get_feature_names_out().tolist()
        except Exception:
            ats_score = 50.0
            keywords = []

        # Skill match
        matched = [s for s in USER_CORE_SKILLS if s in jd_lower and s in resume_lower]
        required = [s for s in USER_CORE_SKILLS if s in jd_lower]
        missing = [s for s in required if s not in resume_lower]
        skill_match_pct = (len(matched) / len(required) * 100) if required else 80.0

        # Missing JD keywords not in resume
        jd_keywords_not_in_resume = [
            kw for kw in keywords if kw not in resume_lower
        ][:10]
        missing_keywords = list(set(missing + jd_keywords_not_in_resume))[:12]

        return {
            "ats_score": ats_score,
            "skill_match_pct": round(skill_match_pct, 1),
            "missing_keywords": missing_keywords,
            "technical_alignment": "Keyword-based analysis (no AI key configured)",
            "experience_alignment": "Keyword-based analysis (no AI key configured)",
            "tailored_bullets": [],
            "tailored_summary": "",
            "cover_letter": "",
            "outreach_message": "",
            "linkedin_message": "",
            "interview_topics": [],
            "skill_gaps": missing[:5],
            "ai_available": False,
        }


# ── Claude-powered analyzer ──────────────────────────────────────────────────

ANALYSIS_PROMPT_TEMPLATE = """\
You are an expert ATS resume optimizer, technical recruiter, and career coach specializing in data analytics roles.

MASTER RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

Analyze the resume against the job description and return ONLY a valid JSON object (no markdown, no explanation) with these exact fields:

{{
  "ats_score": <integer 0-100 — overall ATS keyword and relevance score>,
  "skill_match_pct": <float — percentage of required skills present in resume>,
  "missing_keywords": <list of strings — important keywords/skills in JD not in resume>,
  "technical_alignment": "<2-3 sentence assessment of technical skills match>",
  "experience_alignment": "<2-3 sentence assessment of experience level and domain match>",
  "tailored_bullets": [
    "<5 improved resume bullet points that emphasize measurable impact for THIS specific role>"
  ],
  "tailored_summary": "<3-sentence professional summary optimized for this role with ATS keywords>",
  "cover_letter": "<3-paragraph cover letter — opening hook, skills+impact evidence, closing call to action>",
  "outreach_message": "<recruiter cold outreach email under 100 words — specific, confident, not generic>",
  "linkedin_message": "<LinkedIn connection request under 50 words>",
  "interview_topics": ["<top 5 likely interview topics based on JD requirements>"],
  "skill_gaps": ["<up to 5 skills to develop to be fully competitive for this role>"],
  "why_it_fits": "<1-2 sentence summary of why this is a good fit>"
}}

Focus on: SQL, Python, Tableau, Power BI, ETL pipelines, Snowflake, AWS, Salesforce/ERP integrations,
dashboard automation, KPI reporting, forecasting, data validation, analytics engineering.
Emphasize measurable impact in bullets: reduced reporting time, improved accuracy, automated workflows, built scalable pipelines."""


class ClaudeATSAnalyzer:
    """Claude claude-sonnet-4-6 powered ATS analysis with structured JSON output."""

    def __init__(self):
        import anthropic
        self.client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

    def analyze(self, resume_text: str, job_description: str) -> dict:
        prompt = ANALYSIS_PROMPT_TEMPLATE.format(
            resume_text=resume_text[:6000],  # stay within context limits
            job_description=job_description[:4000],
        )
        try:
            message = self.client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=2048,
                messages=[{"role": "user", "content": prompt}],
            )
            raw = message.content[0].text.strip()
            # Strip any accidental markdown fences
            raw = re.sub(r"^```(?:json)?\s*", "", raw)
            raw = re.sub(r"\s*```$", "", raw)
            result = json.loads(raw)
            result["ai_available"] = True
            return result
        except json.JSONDecodeError as e:
            logger.error(f"Claude returned invalid JSON: {e}")
            raise
        except Exception as e:
            logger.error(f"Claude API error: {e}")
            raise


# ── Public interface ──────────────────────────────────────────────────────────

class ATSAnalysisService:
    """
    Entry point for ATS analysis.
    Routes to Claude if API key is set, otherwise uses TF-IDF fallback.
    """

    def __init__(self):
        if settings.ANTHROPIC_API_KEY:
            self._analyzer = ClaudeATSAnalyzer()
            self.ai_available = True
        else:
            logger.info("ANTHROPIC_API_KEY not set — using fallback TF-IDF ATS scoring")
            self._analyzer = FallbackATSAnalyzer()
            self.ai_available = False

    def analyze(self, resume_text: str, job_description: str) -> dict:
        """Analyze a single job description against the master resume."""
        if not resume_text or not job_description:
            return {
                "ats_score": 0.0, "skill_match_pct": 0.0, "missing_keywords": [],
                "ai_available": self.ai_available,
            }
        return self._analyzer.analyze(resume_text, job_description)

    def batch_analyze(
        self, resume_text: str, job_descriptions: list[tuple[int, str]], delay_seconds: float = 1.0
    ) -> dict[int, dict]:
        """
        Analyze multiple jobs against one resume.
        Returns {job_id: analysis_dict}.
        Rate-limits with delay_seconds between Claude calls.
        """
        results = {}
        for job_id, description in job_descriptions:
            try:
                result = self.analyze(resume_text, description)
                results[job_id] = result
                if self.ai_available:
                    time.sleep(delay_seconds)
            except Exception as e:
                logger.error(f"ATS analysis failed for job {job_id}: {e}")
                results[job_id] = {"ats_score": None, "error": str(e)}
        return results
