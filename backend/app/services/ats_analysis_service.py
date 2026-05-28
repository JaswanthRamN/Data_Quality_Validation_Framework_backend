"""
ATS analysis service — provider-agnostic resume-vs-JD matching.

Configure AI_PROVIDER in .env:
  gemini      → Google Gemini 1.5 Flash (free 1,500 req/day)
  groq        → Groq Llama 3.3-70b (free ~14,400 req/day, very fast)
  openai      → OpenAI GPT-4o-mini (~$0.01 per 10 analyses)
  huggingface → HuggingFace Inference API (free tier)
  ollama      → Local Ollama (completely free)
  anthropic   → Anthropic Claude Sonnet
  none        → TF-IDF keyword fallback only (no AI features)
"""

import logging
import time
from typing import Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.config import settings
from app.services.llm_provider import get_llm_provider

logger = logging.getLogger(__name__)

USER_CORE_SKILLS = [
    "sql", "python", "tableau", "power bi", "etl", "pipeline", "snowflake",
    "aws", "salesforce", "erp", "dashboard", "kpi", "forecasting",
    "data validation", "analytics", "reporting", "visualization",
    "excel", "dbt", "airflow", "spark", "looker", "data warehouse",
    "redshift", "postgresql", "mysql", "regression", "a/b testing",
]

ANALYSIS_PROMPT = """\
You are an expert ATS resume optimizer, technical recruiter, and career coach specializing in data analytics roles.

MASTER RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

Analyze the resume against the job description and return ONLY a valid JSON object (no markdown, no explanation) with these exact fields:

{{
  "ats_score": <integer 0-100 — overall ATS keyword and relevance score>,
  "skill_match_pct": <float — percentage of required skills present in resume>,
  "missing_keywords": ["<keywords/skills in JD not in resume>"],
  "technical_alignment": "<2-3 sentence assessment of technical skills match>",
  "experience_alignment": "<2-3 sentence assessment of experience level and domain match>",
  "tailored_bullets": [
    "<5 improved resume bullet points emphasizing measurable impact for THIS specific role>"
  ],
  "tailored_summary": "<3-sentence professional summary optimized for this role with ATS keywords>",
  "cover_letter": "<3-paragraph cover letter: opening hook, skills+impact evidence, closing call to action>",
  "outreach_message": "<recruiter cold outreach email under 100 words — specific, confident, not generic>",
  "linkedin_message": "<LinkedIn connection request under 50 words>",
  "interview_topics": ["<top 5 likely interview topics based on JD requirements>"],
  "skill_gaps": ["<up to 5 skills to develop to be fully competitive for this role>"],
  "why_it_fits": "<1-2 sentence summary of why this is a good fit>"
}}

User background: SQL (Advanced), Python, Power BI, Tableau, ETL/ELT, dbt, Airflow, Snowflake, Redshift, PostgreSQL, AWS (S3, Lambda), Salesforce, ERP (SAP, NetSuite), KPI reporting, forecasting, data validation, analytics engineering.
Emphasize measurable impact in bullets: reduced reporting time, improved accuracy %, automated workflows, built scalable pipelines, cost savings."""


# ── TF-IDF fallback (no API key / AI_PROVIDER=none) ──────────────────────────

class FallbackATSAnalyzer:
    """Keyword-based scoring — works offline, no API key required."""

    def analyze(self, resume_text: str, job_description: str) -> dict:
        resume_lower = resume_text.lower()
        jd_lower = job_description.lower()

        try:
            vectorizer = TfidfVectorizer(
                stop_words="english", ngram_range=(1, 2), max_features=50
            )
            matrix = vectorizer.fit_transform([jd_lower, resume_lower])
            similarity = cosine_similarity(matrix[0:1], matrix[1:2])[0][0]
            ats_score = round(float(similarity) * 100, 1)
            keywords = vectorizer.get_feature_names_out().tolist()
        except Exception:
            ats_score = 50.0
            keywords = []

        required = [s for s in USER_CORE_SKILLS if s in jd_lower]
        matched = [s for s in required if s in resume_lower]
        missing = [s for s in required if s not in resume_lower]
        skill_match_pct = (len(matched) / len(required) * 100) if required else 80.0

        extra_missing = [kw for kw in keywords if kw not in resume_lower][:10]
        missing_keywords = list(dict.fromkeys(missing + extra_missing))[:12]

        return {
            "ats_score": ats_score,
            "skill_match_pct": round(skill_match_pct, 1),
            "missing_keywords": missing_keywords,
            "technical_alignment": "Keyword-based analysis (configure AI_PROVIDER in .env for full analysis)",
            "experience_alignment": "Keyword-based analysis (configure AI_PROVIDER in .env for full analysis)",
            "tailored_bullets": [],
            "tailored_summary": "",
            "cover_letter": "",
            "outreach_message": "",
            "linkedin_message": "",
            "interview_topics": [],
            "skill_gaps": missing[:5],
            "why_it_fits": "",
            "ai_available": False,
        }


# ── AI-powered analyzer ───────────────────────────────────────────────────────

class AIATSAnalyzer:
    """Uses whichever LLMProvider is configured to produce full ATS analysis."""

    def __init__(self, provider):
        self._provider = provider

    def analyze(self, resume_text: str, job_description: str) -> dict:
        prompt = ANALYSIS_PROMPT.format(
            resume_text=resume_text[:6000],
            job_description=job_description[:4000],
        )
        result = self._provider.complete_json(prompt, max_tokens=2048)
        result.setdefault("ai_available", True)
        return result


# ── Public service ────────────────────────────────────────────────────────────

class ATSAnalysisService:
    """
    Entry point for ATS analysis.
    Automatically selects the right analyzer based on AI_PROVIDER config.
    """

    def __init__(self):
        provider = get_llm_provider()
        if provider is not None:
            self._analyzer = AIATSAnalyzer(provider)
            self.ai_available = True
            self.provider_name = settings.AI_PROVIDER
        else:
            self._analyzer = FallbackATSAnalyzer()
            self.ai_available = False
            self.provider_name = "none"
            logger.info(
                f"AI_PROVIDER={settings.AI_PROVIDER!r} — using TF-IDF fallback. "
                "Set AI_PROVIDER and the matching API key in .env to enable full analysis."
            )

    def analyze(self, resume_text: str, job_description: str) -> dict:
        if not resume_text or not job_description:
            return {
                "ats_score": 0.0, "skill_match_pct": 0.0,
                "missing_keywords": [], "ai_available": self.ai_available,
            }
        try:
            return self._analyzer.analyze(resume_text, job_description)
        except Exception as e:
            logger.error(f"ATS analysis failed ({self.provider_name}): {e}")
            logger.info("Falling back to TF-IDF for this job")
            return FallbackATSAnalyzer().analyze(resume_text, job_description)

    def batch_analyze(
        self,
        resume_text: str,
        job_descriptions: list[tuple[int, str]],
        delay_seconds: float = 1.0,
    ) -> dict[int, dict]:
        """
        Analyze multiple jobs. Returns {job_id: analysis_dict}.
        Applies delay between AI calls to respect rate limits.
        """
        results = {}
        for job_id, description in job_descriptions:
            results[job_id] = self.analyze(resume_text, description)
            if self.ai_available:
                time.sleep(delay_seconds)
        return results
