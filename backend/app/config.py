"""
Configuration module for loading environment variables and app settings.
Uses Pydantic for validation and type safety.
"""

from pydantic_settings import BaseSettings
from typing import Optional, List
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API Settings
    API_TITLE: str = "Data Quality Validation Framework"
    API_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Database Settings
    DATABASE_URL: str
    DATABASE_ECHO: bool = False
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10
    DATABASE_POOL_PRE_PING: bool = True
    DATABASE_POOL_RECYCLE: int = 3600

    # Security Settings
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS Settings
    CORS_ORIGINS: list = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list = ["*"]
    CORS_ALLOW_HEADERS: list = ["*"]

    # Logging Settings
    LOG_LEVEL: str = "INFO"
    LOG_FILE: Optional[str] = None

    # Feature Flags
    ENABLE_ASYNC_TASKS: bool = True
    ENABLE_CACHING: bool = True

    # Celery Settings
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

    # Redis Caching Settings
    REDIS_ENABLED: bool = True
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    REDIS_SOCKET_TIMEOUT: int = 5
    REDIS_VALIDATION_TTL: int = 1800  # 30 minutes
    REDIS_METRICS_TTL: int = 3600  # 1 hour
    REDIS_DATASET_TTL: int = 7200  # 2 hours
    REDIS_ANOMALY_TTL: int = 1800  # 30 minutes
    REDIS_SESSION_TTL: int = 86400  # 24 hours

    # ── Job Search Automation ────────────────────────────────────────────────

    # AI Provider selection — controls which LLM powers ATS analysis.
    # Options: gemini | groq | openai | huggingface | ollama | anthropic | none
    # Set the matching API key below. If key is missing, falls back to TF-IDF scoring.
    AI_PROVIDER: str = "none"

    # Google Gemini — free 1,500 req/day  →  https://ai.google.dev
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.0-flash"

    # Groq — free ~14,400 req/day (Llama 3)  →  https://console.groq.com
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    # OpenAI — pay-as-you-go, gpt-4o-mini ~$0.01 per 10 analyses
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"

    # HuggingFace Inference API — free tier  →  https://huggingface.co/settings/tokens
    HUGGINGFACE_API_KEY: str = ""
    HUGGINGFACE_MODEL: str = "mistralai/Mistral-7B-Instruct-v0.3"

    # Ollama — local, completely free  →  https://ollama.ai  then: ollama pull llama3.2
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.2"

    # Anthropic Claude — original option
    ANTHROPIC_API_KEY: str = ""

    # Master resume text — paste full resume here (supports multiline via env file)
    MASTER_RESUME_TEXT: str = (
        "Jaswanth Ram Nagabhyrava | Data Analyst | Baltimore, MD | "
        "Skills: SQL (Advanced), Python (Pandas, NumPy), Power BI, Tableau, "
        "ETL/ELT Pipelines, dbt, Apache Airflow, Snowflake, Redshift, PostgreSQL, "
        "MySQL, SQL Server, AWS (S3, Lambda), Salesforce, ERP (SAP, NetSuite), "
        "Time Series Forecasting, Regression Analysis, A/B Testing, "
        "Git, Docker, Jira, Data Quality Checks, KPI Tracking, Dashboard Development. "
        "Experience: Data Analyst at Rishi Inc (Mar 2024-Present) — Built Power BI dashboards "
        "reducing manual reporting by 45%; designed SQL pipelines integrating Salesforce and ERP "
        "processing 500K+ records/month improving accuracy by 30%; developed Python ETL workflows; "
        "implemented automated refresh pipelines with data quality checks. "
        "Data Analyst at Pioneer Auto World (Aug 2021-Dec 2022) — Consolidated sales/service/inventory "
        "datasets cutting reporting prep by 60%; built Tableau dashboards improving operational visibility "
        "by 40%; applied time-series forecasting improving planning accuracy by 25%; automated monthly "
        "reporting from 3 hours to 20 minutes; delivered $28K quarterly cost savings. "
        "Education: MS Information Systems UMBC. "
        "Projects: Baltimore Crime Analysis (1M+ records, 90% reporting reduction), "
        "F1 Lap Time Prediction (93% R2), Off-Task Behavior Prediction (ML, Flask, F1 +12%)."
    )

    # Job search target configuration
    JOB_TARGET_ROLES: List[str] = [
        "Data Analyst",
        "Business Intelligence Analyst",
        "Business Analyst",
        "Product Analyst",
        "Reporting Analyst",
        "Analytics Engineer",
        "Operations Analyst",
        "Revenue Operations Analyst",
        "Supply Chain Analyst",
        "Procurement Analyst",
    ]
    JOB_TARGET_LOCATIONS: List[str] = [
        "remote",
        "California",
        "Washington",
        "Oregon",
        "Colorado",
        "Texas",
        "Illinois",
        "Virginia",
        "New York",
        "New Jersey",
        "Massachusetts",
        "Maryland",
        "Georgia",
        "Utah",
        "Minnesota",
    ]
    JOB_EXCLUSION_KEYWORDS: List[str] = [
        "security clearance",
        "clearance required",
        "secret clearance",
        "top secret",
        "ITAR",
        "US citizen only",
        "must be a US citizen",
        "public trust",
        "government only",
        "C2C only",
        "corp to corp only",
    ]
    JOB_SPONSORSHIP_KEYWORDS: List[str] = [
        "sponsor",
        "h1b",
        "h-1b",
        "visa sponsorship",
        "work authorization",
        "OPT",
        "CPT",
    ]

    # Composite scoring weights (must sum to 1.0)
    SCORE_WEIGHT_ATS: float = 0.30
    SCORE_WEIGHT_SPONSORSHIP: float = 0.20
    SCORE_WEIGHT_REMOTE: float = 0.15
    SCORE_WEIGHT_SALARY: float = 0.15
    SCORE_WEIGHT_SKILLS: float = 0.10
    SCORE_WEIGHT_COMPANY: float = 0.05
    SCORE_WEIGHT_GROWTH: float = 0.05

    # Salary normalization band for scoring (USD)
    SALARY_SCORE_MIN: float = 80000.0
    SALARY_SCORE_MAX: float = 160000.0

    # Notion job tracking database ID (populated after first run)
    NOTION_JOB_DATABASE_ID: str = ""

    class Config:
        env_file = ".env"
        case_sensitive = True


# Load settings once
settings = Settings()
