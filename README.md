# Data Quality Validation Framework - Backend API

A comprehensive FastAPI-based data quality validation framework with JWT authentication, role-based access control, and multi-method data validation capabilities.

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
- [Authentication](#authentication)
- [Database Models](#database-models)
- [API Endpoints](#api-endpoints)
- [Development](#development)
- [Contributing](#contributing)
- [License](#license)

## Features

✅ **JWT Authentication**
- Secure user registration and login
- Access token and refresh token management
- Password hashing with bcrypt
- Account activation/deactivation

✅ **Role-Based Access Control (RBAC)**
- Admin and user roles
- Permission-based endpoint access
- Dataset ownership tracking
- User-specific validation history

✅ **Data Quality Validation**
- Multiple validation methods (Z-score, IQR, custom rules)
- Anomaly detection
- Data reconciliation
- Quality metrics calculation
- Validation caching

✅ **Dataset Management**
- Dataset creation and organization
- Multi-format support (CSV, JSON, Parquet, Excel, Database)
- File ingestion and processing
- Dataset metadata tracking

✅ **Caching & Performance**
- Redis-based caching layer
- TTL-based cache invalidation
- Performance optimization
- Async task processing

✅ **Security**
- CORS configuration
- Trusted host middleware
- Request logging and monitoring
- SQL injection prevention
- Secure password management

✅ **Comprehensive Logging**
- Structured logging
- Separate log files for different components
- Error tracking and debugging
- Audit trail for authentication events

## Architecture

```
backend/
├── app/
│   ├── api/                    # API route modules
│   │   ├── auth_routes.py     # Authentication endpoints
│   │   ├── dataset_routes.py  # Dataset management endpoints
│   │   ├── validation_routes.py # Validation endpoints
│   │   └── router.py          # Route aggregator
│   ├── core/
│   │   ├── security.py        # JWT and password utilities
│   │   ├── cache.py           # Redis cache management
│   │   └── middleware.py      # FastAPI middleware setup
│   ├── crud/                   # Database operations
│   │   ├── user_crud.py       # User CRUD operations
│   │   ├── dataset_crud.py    # Dataset CRUD operations
│   │   └── validation_crud.py # Validation CRUD operations
│   ├── models/                 # SQLAlchemy ORM models
│   │   ├── base.py            # Base model classes
│   │   ├── user.py            # User model
│   │   ├── dataset.py         # Dataset model
│   │   └── validation_result.py # Validation result model
│   ├── schemas/                # Pydantic validation schemas
│   │   ├── auth_schema.py     # Auth request/response models
│   │   ├── dataset_schema.py  # Dataset models
│   │   └── validation_schema.py # Validation models
│   ├── services/               # Business logic layer
│   ├── anomaly_detection/      # Anomaly detection algorithms
│   ├── validation/             # Validation engines and rules
│   ├── utils/
│   │   ├── logger.py          # Logging configuration
│   │   └── file_handler.py    # File utilities
│   ├── config.py              # Configuration management
│   ├── database.py            # Database connection
│   ├── dependencies.py        # Dependency injection
│   └── main.py                # FastAPI app initialization
├── migrations/                 # Alembic database migrations
├── logs/                       # Application logs
├── data_sources/              # Uploaded data files
├── requirements.txt           # Python dependencies
├── .env.example               # Environment variables template
└── docker-compose.yml         # Docker orchestration
```

## Requirements

- Python 3.9+
- PostgreSQL 12+
- Redis 6+
- Docker & Docker Compose (optional)

## Installation

### Prerequisites

1. **Clone the repository:**
```bash
git clone <repository-url>
cd backend
```

2. **Create a Python virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Setup Steps

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Configure environment variables:**
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Create PostgreSQL database:**
```bash
createdb data_quality_db
# Or use your PostgreSQL client of choice
```

4. **Initialize database schema:**
```bash
python -m alembic upgrade head
# Or the database tables will be auto-created on first run
```

5. **Verify installation:**
```bash
python -c "import app; print('Installation successful!')"
```

## Configuration

### Environment Variables

Create a `.env` file in the `backend` directory based on `.env.example`:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/data_quality_db

# Security (generate a strong SECRET_KEY)
SECRET_KEY=your-super-secret-key-change-this
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Redis (for caching)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
```

### Generate Secret Key

```python
import secrets
print(secrets.token_urlsafe(32))
```

## Running the Application

### Development Mode

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: http://localhost:8000

### Production Mode

```bash
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Using Docker

```bash
docker-compose up -d
```

## API Documentation

### Interactive Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## Authentication

### User Registration

**Endpoint:** `POST /api/auth/register`

```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "SecurePassword123!",
  "full_name": "John Doe"
}
```

**Response:**
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "full_name": "John Doe",
  "is_active": true
}
```

### User Login

**Endpoint:** `POST /api/auth/login`

```json
{
  "username": "john_doe",
  "password": "SecurePassword123!"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### Using Access Token

Include the access token in the `Authorization` header for authenticated requests:

```bash
curl -H "Authorization: Bearer <access_token>" http://localhost:8000/api/datasets/
```

### Refresh Token

**Endpoint:** `POST /api/auth/refresh`

```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

## Database Models

### User Model

```python
class User:
    id: int (Primary Key)
    username: str (Unique)
    email: str (Unique)
    full_name: str (Optional)
    hashed_password: str
    is_active: bool
    is_admin: bool
    created_at: datetime
    updated_at: datetime
    last_login: datetime (Optional)
```

### Dataset Model

```python
class Dataset:
    id: int (Primary Key)
    name: str (Unique)
    description: str (Optional)
    source_type: str (csv, json, parquet, database)
    file_path: str (Optional)
    record_count: int
    column_count: int
    created_by: int (Foreign Key → User.id)
    created_at: datetime
    updated_at: datetime
    is_active: int
```

### ValidationResult Model

```python
class ValidationResult:
    id: int (Primary Key)
    dataset_id: int (Foreign Key → Dataset.id)
    validation_type: str
    status: str (PASSED, FAILED, WARNING)
    passed_count: int
    failed_count: int
    pass_rate: float
    error_message: str (Optional)
    errors: JSON (Optional)
    validation_details: JSON (Optional)
    created_by: int (Foreign Key → User.id)
    execution_time_ms: float
    created_at: datetime
    updated_at: datetime
```

## API Endpoints

### Authentication

- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `POST /api/auth/refresh` - Refresh access token
- `GET /api/auth/me` - Get current user info
- `POST /api/auth/change-password` - Change user password

### Datasets (Requires Authentication)

- `POST /api/datasets/` - Create dataset
- `GET /api/datasets/` - List user's datasets
- `GET /api/datasets/{dataset_id}` - Get dataset details
- `DELETE /api/datasets/{dataset_id}` - Delete dataset
- `GET /api/datasets/user/{username}/datasets` - Get user's datasets (Admin)

### Validations (Requires Authentication)

- `POST /api/validations/` - Create validation
- `GET /api/validations/` - List validations
- `GET /api/validations/{validation_id}` - Get validation details
- `DELETE /api/validations/{validation_id}` - Delete validation
- `GET /api/validations/dataset/{dataset_id}/results` - Get dataset validations

### Health & Status

- `GET /` - API info and status
- `GET /health` - Health check

## Development

### Running Tests

```bash
pytest tests/ -v
```

### Code Quality

```bash
# Linting
flake8 app/

# Type checking
mypy app/

# Formatting
black app/
```

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## Troubleshooting

### Common Issues

**Port already in use:**
```bash
# Change port
uvicorn app.main:app --port 8001
```

**Database connection error:**
- Verify PostgreSQL is running
- Check DATABASE_URL in .env
- Ensure database exists

**Redis connection error:**
- Verify Redis is running
- Check REDIS_HOST and REDIS_PORT in .env
- Set ENABLE_CACHING=False to disable caching

**Permission denied errors:**
- Check directory permissions
- Ensure logs/ and data_sources/ directories exist
- Create them if needed: `mkdir -p logs data_sources`

## Performance Tips

1. **Use connection pooling** - Configured by default
2. **Enable caching** - Set ENABLE_CACHING=True
3. **Use indexes** - Already configured on frequently queried fields
4. **Monitor logs** - Check logs/ for performance insights
5. **Pagination** - Use skip/limit parameters for large result sets

## Security Best Practices

1. **Change SECRET_KEY** in production
2. **Use HTTPS** - Enable SSL/TLS certificates
3. **Restrict CORS** - Configure allowed origins
4. **Update dependencies** - Keep packages up to date
5. **Strong passwords** - Enforce password complexity
6. **Regular backups** - Backup database regularly
7. **Audit logs** - Monitor authentication events

## Contributing

1. Create a feature branch: `git checkout -b feature/new-feature`
2. Commit changes: `git commit -m "Add new feature"`
3. Push to branch: `git push origin feature/new-feature`
4. Submit a pull request

## License

This project is licensed under the MIT License - see LICENSE file for details.

## Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Contact the development team
- Check documentation at /docs endpoint

## Changelog

### Version 1.0.0 (Initial Release)

- JWT authentication with access/refresh tokens
- Role-based access control (Admin/User)
- Dataset management with ownership tracking
- Validation result tracking
- Redis caching layer
- Comprehensive logging
- Async task support
- Full API documentation

---

**Last Updated:** 2024  
**Maintained By:** Data Quality Team