# Contributing to Data Quality Validation Framework

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

Please be respectful and professional when interacting with other contributors and maintainers.

## Getting Started

### 1. Fork and Clone

```bash
# Fork the repository on GitHub
# Clone your fork
git clone https://github.com/your-username/Data_Quality_Validation_Framework_backend.git
cd Data_Quality_Validation_Framework_backend/backend
```

### 2. Set Up Development Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest pytest-cov black flake8 mypy
```

### 3. Configure Local Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with local settings
```

## Development Workflow

### Creating a Feature Branch

```bash
git checkout -b feature/your-feature-name
# or for bug fixes:
git checkout -b bugfix/issue-description
```

### Writing Code

1. **Follow PEP 8 Style Guide**
   - Use 4 spaces for indentation
   - Keep lines under 100 characters
   - Use meaningful variable names

2. **Add Docstrings**
   ```python
   def function_name(param1: str, param2: int) -> dict:
       """
       Brief description of function.
       
       Args:
           param1: Description
           param2: Description
           
       Returns:
           Description of return value
           
       Raises:
           Exception: When something happens
       """
   ```

3. **Type Hints**
   - Use type hints for all function parameters and return values
   - Use Optional[] for optional parameters

4. **Comments**
   - Use comments to explain why, not what
   - Keep comments up-to-date with code changes

### Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Run specific test file
pytest tests/test_auth.py -v

# Run specific test function
pytest tests/test_auth.py::test_user_registration -v
```

### Code Quality Checks

```bash
# Format code
black app/

# Lint code
flake8 app/ --max-line-length=100

# Type checking
mypy app/
```

## Making Changes

### 1. Create Tests First (TDD)

Write tests for your feature before implementing:

```python
# tests/test_new_feature.py
def test_new_feature():
    """Test description."""
    # Arrange
    expected = "expected value"
    
    # Act
    result = function_under_test()
    
    # Assert
    assert result == expected
```

### 2. Implement Feature

Implement the feature to make the tests pass.

### 3. Run Tests and Quality Checks

```bash
pytest tests/ -v
black app/
flake8 app/
mypy app/
```

### 4. Update Documentation

Update README.md or create new documentation if needed.

## Commit Guidelines

### Commit Messages

Use clear, descriptive commit messages:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation changes
- `refactor`: Code refactoring without feature changes
- `test`: Adding or updating tests
- `chore`: Build, CI, dependencies

**Example:**
```
feat(auth): add JWT token refresh endpoint

Added a new endpoint to refresh expired access tokens using refresh tokens.
This maintains user sessions without requiring re-login.

Closes #123
```

### Commit Best Practices

- Commit frequently with logical, atomic commits
- Each commit should represent one logical change
- Don't mix formatting and functional changes
- Use present tense ("add feature" not "added feature")

## Submitting a Pull Request

### 1. Update Your Branch

```bash
git fetch origin
git rebase origin/main
```

### 2. Push Your Branch

```bash
git push origin feature/your-feature-name
```

### 3. Create Pull Request on GitHub

- Provide a clear title
- Write a detailed description of changes
- Reference related issues (#123)
- Include screenshots if applicable

### PR Template

```markdown
## Description
Brief description of changes.

## Related Issues
Closes #123

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] No new warnings generated
- [ ] Tests pass locally
```

## Pull Request Review

Your PR will be reviewed by maintainers. Please:

1. Respond to feedback promptly
2. Make requested changes in new commits (don't force push)
3. Keep discussions professional and respectful
4. Be open to suggestions and improvements

## Project Structure

```
backend/
├── app/
│   ├── api/              # Route handlers
│   ├── core/             # Core utilities
│   ├── crud/             # Database operations
│   ├── models/           # SQLAlchemy models
│   ├── schemas/          # Pydantic schemas
│   ├── services/         # Business logic
│   ├── utils/            # Utility functions
│   ├── config.py         # Configuration
│   ├── database.py       # Database setup
│   ├── dependencies.py   # DI setup
│   └── main.py           # App initialization
├── tests/                # Test files
├── requirements.txt      # Dependencies
└── README.md            # Documentation
```

## Adding New Features

### 1. Database Models

If adding a new database entity:

```python
# app/models/new_model.py
from app.models.base import Base, IdMixin, TimestampMixin

class NewModel(Base, IdMixin, TimestampMixin):
    """Description of model."""
    __tablename__ = "new_models"
    
    column1 = Column(String, nullable=False)
    column2 = Column(Integer, default=0)
```

### 2. CRUD Operations

```python
# app/crud/new_model_crud.py
def create_new_model(db: Session, **kwargs) -> NewModel:
    """Create new model."""
    db_model = NewModel(**kwargs)
    db.add(db_model)
    db.commit()
    db.refresh(db_model)
    return db_model
```

### 3. Schemas

```python
# app/schemas/new_model_schema.py
class NewModelCreate(BaseModel):
    """Creation schema."""
    field1: str

class NewModelResponse(BaseModel):
    """Response schema."""
    id: int
    field1: str
    
    class Config:
        from_attributes = True
```

### 4. Routes

```python
# app/api/new_model_routes.py
from fastapi import APIRouter

router = APIRouter(prefix="/api/new-models", tags=["new-models"])

@router.post("/", response_model=NewModelResponse)
def create(data: NewModelCreate, db: Session = Depends(get_db)):
    """Create new model."""
    return new_model_crud.create_new_model(db, **data.dict())
```

### 5. Tests

Write comprehensive tests for your feature.

## Release Process

1. Update version in setup.py
2. Update CHANGELOG.md
3. Create git tag: `git tag v1.0.0`
4. Push tag: `git push origin v1.0.0`
5. Create GitHub release

## Questions or Issues?

- Open an issue on GitHub
- Check existing issues and discussions
- Reach out to maintainers

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (MIT License).

Thank you for contributing! 🎉
