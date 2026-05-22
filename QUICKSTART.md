# Quick Start Guide

Get up and running with the Data Quality Validation Framework backend in 5 minutes.

## Prerequisites

- Python 3.9+
- Git
- Docker (optional, for containerized setup)

## Option 1: Local Development Setup

### Step 1: Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd Data_Quality_Validation_Framework_backend/backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit configuration (use any text editor)
# nano .env
```

**Minimum required settings:**
```env
DATABASE_URL=postgresql://user:password@localhost:5432/data_quality_db
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

### Step 3: Setup Database

```bash
# Create PostgreSQL database
# Using command line:
createdb data_quality_db

# Or using PostgreSQL client GUI (pgAdmin, DBeaver, etc.)
```

### Step 4: Run Application

```bash
# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

✅ API is now running at: **http://localhost:8000**

## Option 2: Docker Setup (Recommended)

### Quick Start

```bash
# Navigate to backend directory
cd Data_Quality_Validation_Framework_backend/backend

# Start all services
docker-compose up -d

# Verify services are running
docker-compose ps
```

✅ API is now running at: **http://localhost:8000**

```bash
# Stop services
docker-compose down

# View logs
docker-compose logs -f api
```

## First Steps

### 1. Access API Documentation

Open your browser and visit:
- **Swagger UI (Interactive):** http://localhost:8000/docs
- **ReDoc (Read-only):** http://localhost:8000/redoc

### 2. Register a User

Using curl:
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "SecurePassword123",
    "full_name": "Test User"
  }'
```

Or use the Swagger UI:
1. Go to http://localhost:8000/docs
2. Expand "POST /api/auth/register"
3. Click "Try it out"
4. Enter test data and click "Execute"

### 3. Login and Get Token

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "SecurePassword123"
  }'
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

### 4. Use the Access Token

```bash
# Create a dataset
curl -X POST http://localhost:8000/api/datasets/ \
  -H "Authorization: Bearer <your-access-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Dataset",
    "source_type": "csv",
    "description": "A test dataset",
    "record_count": 1000
  }'

# List datasets
curl -H "Authorization: Bearer <your-access-token>" \
  http://localhost:8000/api/datasets/
```

## Project Structure

```
backend/
├── app/
│   ├── api/              # API endpoints
│   ├── core/             # Core utilities (security, cache)
│   ├── crud/             # Database operations
│   ├── models/           # Database models
│   ├── schemas/          # Request/response schemas
│   ├── config.py         # Configuration
│   ├── database.py       # Database setup
│   └── main.py           # App entry point
├── .env.example          # Environment template
├── requirements.txt      # Dependencies
├── docker-compose.yml    # Docker setup
└── README.md            # Full documentation
```

## Common Tasks

### View API Logs

**Docker:**
```bash
docker-compose logs -f api
```

**Local:**
```bash
tail -f logs/app.log
```

### Access Database

**Docker:**
```bash
# Connect to PostgreSQL
docker-compose exec postgres psql -U data_quality_user -d data_quality_db

# Common commands:
# \dt              - List tables
# \d table_name    - Describe table
# SELECT * FROM users;  - Query data
```

### Stop Services

**Docker:**
```bash
docker-compose down
```

**Local:**
- Press `Ctrl+C` in the terminal running uvicorn

### Reset Database

**Docker:**
```bash
# Remove all data
docker-compose down -v

# Restart fresh
docker-compose up -d
```

**Local:**
```bash
# Drop database
dropdb data_quality_db

# Recreate
createdb data_quality_db

# Restart server
```

## Troubleshooting

### Port Already in Use

```bash
# Use different port
uvicorn app.main:app --port 8001

# Or kill process using port 8000
# On macOS/Linux:
lsof -i :8000 | grep LISTEN | awk '{print $2}' | xargs kill -9

# On Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Database Connection Error

1. Check PostgreSQL is running:
   ```bash
   # macOS with Homebrew:
   brew services list | grep postgres
   
   # Linux:
   sudo systemctl status postgresql
   ```

2. Verify DATABASE_URL in .env
3. Ensure database exists: `psql -l | grep data_quality`

### Redis Connection Error (Optional)

If caching is enabled but Redis isn't available:
1. Start Redis: `redis-server`
2. Or disable: Set `ENABLE_CACHING=False` in .env

### Import Errors

```bash
# Ensure virtual environment is activated
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

## Next Steps

1. **Read the full documentation:** See [README.md](README.md)
2. **Explore API endpoints:** Visit http://localhost:8000/docs
3. **Run tests:** `pytest tests/ -v`
4. **Deploy:** See [DEPLOYMENT.md](DEPLOYMENT.md)
5. **Contribute:** See [CONTRIBUTING.md](CONTRIBUTING.md)

## Key API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register new user |
| POST | `/api/auth/login` | Login user |
| GET | `/api/auth/me` | Get current user |
| POST | `/api/datasets/` | Create dataset |
| GET | `/api/datasets/` | List datasets |
| POST | `/api/validations/` | Create validation |
| GET | `/api/validations/` | List validations |
| GET | `/health` | Health check |

## Support

- 📖 [Full Documentation](README.md)
- 🐳 [Deployment Guide](DEPLOYMENT.md)
- 🤝 [Contributing Guidelines](CONTRIBUTING.md)
- 📝 [API Docs](http://localhost:8000/docs)

---

Happy coding! 🚀
