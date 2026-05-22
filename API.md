# API Specification

Complete API specification for the Data Quality Validation Framework backend.

## Base URL

```
http://localhost:8000/api
https://api.yourdomain.com/api  (Production)
```

## Authentication

All protected endpoints require JWT token in the `Authorization` header:

```
Authorization: Bearer <access_token>
```

## Response Format

All responses are in JSON format:

**Success Response:**
```json
{
  "data": {...},
  "status": 200,
  "message": "Success"
}
```

**Error Response:**
```json
{
  "detail": "Error message",
  "status": 400,
  "error_code": "VALIDATION_ERROR"
}
```

## Authentication Endpoints

### Register User

**Endpoint:** `POST /auth/register`

**Description:** Register a new user account

**Request Body:**
```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "SecurePassword123!",
  "full_name": "John Doe"
}
```

**Request Parameters:**
| Field | Type | Required | Min | Max | Notes |
|-------|------|----------|-----|-----|-------|
| username | string | ✓ | 3 | 50 | Unique, alphanumeric |
| email | string | ✓ | - | - | Valid email format |
| password | string | ✓ | 8 | - | Min 8 characters |
| full_name | string | - | - | 100 | Optional |

**Success Response (201):**
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "full_name": "John Doe",
  "is_active": true
}
```

**Error Responses:**
- `400 Bad Request` - Username or email already exists
- `422 Unprocessable Entity` - Invalid input data

---

### Login

**Endpoint:** `POST /auth/login`

**Description:** Authenticate user and receive tokens

**Request Body:**
```json
{
  "username": "john_doe",
  "password": "SecurePassword123!"
}
```

**Request Parameters:**
| Field | Type | Required | Notes |
|-------|------|----------|-------|
| username | string | ✓ | Username or email |
| password | string | ✓ | User password |

**Success Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

**Error Responses:**
- `401 Unauthorized` - Invalid credentials
- `403 Forbidden` - Account is inactive

---

### Refresh Token

**Endpoint:** `POST /auth/refresh`

**Description:** Get new access token using refresh token

**Request Body:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Success Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

**Error Responses:**
- `401 Unauthorized` - Invalid or expired refresh token

---

### Get Current User

**Endpoint:** `GET /auth/me`

**Description:** Get current authenticated user information

**Authentication:** Required ✓

**Success Response (200):**
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "full_name": "John Doe",
  "is_active": true
}
```

**Error Responses:**
- `401 Unauthorized` - Invalid or missing token

---

### Change Password

**Endpoint:** `POST /auth/change-password`

**Description:** Change user password

**Authentication:** Required ✓

**Request Body:**
```json
{
  "old_password": "OldPassword123!",
  "new_password": "NewPassword456!"
}
```

**Request Parameters:**
| Field | Type | Required | Min | Notes |
|-------|------|----------|-----|-------|
| old_password | string | ✓ | 6 | Current password |
| new_password | string | ✓ | 8 | New password |

**Success Response (200):**
```json
{
  "message": "Password changed successfully"
}
```

**Error Responses:**
- `401 Unauthorized` - Invalid old password
- `422 Unprocessable Entity` - Validation error

---

## Dataset Endpoints

### Create Dataset

**Endpoint:** `POST /datasets/`

**Description:** Create a new dataset

**Authentication:** Required ✓

**Request Body:**
```json
{
  "name": "Sales Data Q1",
  "source_type": "csv",
  "description": "Q1 sales information",
  "file_path": "/data_sources/sales_q1.csv",
  "record_count": 5000,
  "column_count": 15
}
```

**Request Parameters:**
| Field | Type | Required | Min | Max | Notes |
|-------|------|----------|-----|-----|-------|
| name | string | ✓ | 1 | 255 | Unique dataset name |
| source_type | string | ✓ | - | 50 | csv, json, parquet, database |
| description | string | - | - | 500 | Optional description |
| file_path | string | - | - | 500 | Path to source file |
| record_count | integer | - | 0 | - | Non-negative |
| column_count | integer | - | 0 | - | Non-negative |

**Success Response (201):**
```json
{
  "id": 1,
  "name": "Sales Data Q1",
  "source_type": "csv",
  "description": "Q1 sales information",
  "file_path": "/data_sources/sales_q1.csv",
  "record_count": 5000,
  "column_count": 15,
  "created_by": 1,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z",
  "is_active": 1
}
```

**Error Responses:**
- `400 Bad Request` - Dataset name already exists
- `401 Unauthorized` - Invalid token
- `500 Internal Server Error` - Database error

---

### List Datasets

**Endpoint:** `GET /datasets/`

**Description:** List all datasets (user's own or all for admin)

**Authentication:** Required ✓

**Query Parameters:**
| Parameter | Type | Default | Max | Notes |
|-----------|------|---------|-----|-------|
| skip | integer | 0 | - | Records to skip (pagination) |
| limit | integer | 100 | 1000 | Records to return |

**Example:**
```
GET /datasets/?skip=0&limit=50
```

**Success Response (200):**
```json
[
  {
    "id": 1,
    "name": "Sales Data Q1",
    "source_type": "csv",
    "description": "Q1 sales information",
    "file_path": "/data_sources/sales_q1.csv",
    "record_count": 5000,
    "column_count": 15,
    "created_by": 1,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z",
    "is_active": 1
  }
]
```

**Error Responses:**
- `401 Unauthorized` - Invalid token

---

### Get Dataset by ID

**Endpoint:** `GET /datasets/{dataset_id}`

**Description:** Get specific dataset details

**Authentication:** Required ✓

**Path Parameters:**
| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| dataset_id | integer | ✓ | Dataset ID |

**Success Response (200):**
```json
{
  "id": 1,
  "name": "Sales Data Q1",
  "source_type": "csv",
  "description": "Q1 sales information",
  "file_path": "/data_sources/sales_q1.csv",
  "record_count": 5000,
  "column_count": 15,
  "created_by": 1,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z",
  "is_active": 1
}
```

**Error Responses:**
- `401 Unauthorized` - Invalid token
- `403 Forbidden` - No permission to access dataset
- `404 Not Found` - Dataset not found

---

### Delete Dataset

**Endpoint:** `DELETE /datasets/{dataset_id}`

**Description:** Delete a dataset

**Authentication:** Required ✓

**Path Parameters:**
| Parameter | Type | Required |
|-----------|------|----------|
| dataset_id | integer | ✓ |

**Success Response (200):**
```json
{
  "message": "Dataset deleted successfully",
  "dataset_id": 1
}
```

**Error Responses:**
- `401 Unauthorized` - Invalid token
- `403 Forbidden` - No permission to delete
- `404 Not Found` - Dataset not found

---

## Validation Endpoints

### Create Validation

**Endpoint:** `POST /validations/`

**Description:** Create validation result for a dataset

**Authentication:** Required ✓

**Request Body:**
```json
{
  "dataset_id": 1,
  "validation_type": "data_quality",
  "status": "PASSED",
  "passed_count": 4950,
  "failed_count": 50,
  "pass_rate": 99.0,
  "error_message": null,
  "validation_details": {
    "rules": ["null_check", "type_check", "range_check"],
    "duration": "2.5s"
  },
  "execution_time_ms": 2500.0
}
```

**Request Parameters:**
| Field | Type | Required | Options | Notes |
|-------|------|----------|---------|-------|
| dataset_id | integer | ✓ | - | Must have access |
| validation_type | string | ✓ | - | Type of validation |
| status | string | ✓ | PASSED, FAILED, WARNING | Result status |
| passed_count | integer | - | 0+ | Number passed |
| failed_count | integer | - | 0+ | Number failed |
| pass_rate | float | - | 0-100 | Pass percentage |
| error_message | string | - | - | Error details |
| validation_details | object | - | - | Detailed results |
| execution_time_ms | float | - | 0+ | Time in milliseconds |

**Success Response (201):**
```json
{
  "id": 1,
  "dataset_id": 1,
  "validation_type": "data_quality",
  "status": "PASSED",
  "passed_count": 4950,
  "failed_count": 50,
  "pass_rate": 99.0,
  "error_message": null,
  "created_by": 1,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z",
  "execution_time_ms": 2500.0
}
```

**Error Responses:**
- `401 Unauthorized` - Invalid token
- `403 Forbidden` - No permission to validate dataset
- `404 Not Found` - Dataset not found

---

### List Validations

**Endpoint:** `GET /validations/`

**Description:** List validations

**Authentication:** Required ✓

**Query Parameters:**
| Parameter | Type | Notes |
|-----------|------|-------|
| dataset_id | integer | Filter by dataset (optional) |
| skip | integer | Records to skip |
| limit | integer | Records to return (max 1000) |

**Success Response (200):**
```json
[
  {
    "id": 1,
    "dataset_id": 1,
    "validation_type": "data_quality",
    "status": "PASSED",
    "passed_count": 4950,
    "failed_count": 50,
    "pass_rate": 99.0,
    "created_by": 1,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z",
    "execution_time_ms": 2500.0
  }
]
```

---

### Get Dataset Validations

**Endpoint:** `GET /validations/dataset/{dataset_id}/results`

**Description:** Get all validation results for a dataset

**Authentication:** Required ✓

**Path Parameters:**
| Parameter | Type | Required |
|-----------|------|----------|
| dataset_id | integer | ✓ |

**Success Response (200):**
```json
[
  {
    "id": 1,
    "dataset_id": 1,
    "validation_type": "data_quality",
    "status": "PASSED",
    "pass_rate": 99.0,
    "created_at": "2024-01-15T10:30:00Z"
  }
]
```

---

## Health Endpoints

### API Status

**Endpoint:** `GET /`

**Description:** Get API status and information

**Success Response (200):**
```json
{
  "title": "Data Quality Validation Framework",
  "version": "1.0.0",
  "status": "running",
  "docs": "/docs",
  "redoc": "/redoc"
}
```

---

### Health Check

**Endpoint:** `GET /health`

**Description:** Verify API is operational

**Success Response (200):**
```json
{
  "status": "healthy",
  "service": "Data Quality Validation Framework",
  "version": "1.0.0"
}
```

---

## Status Codes

| Code | Name | Meaning |
|------|------|---------|
| 200 | OK | Request successful |
| 201 | Created | Resource created |
| 400 | Bad Request | Invalid input |
| 401 | Unauthorized | Auth required/failed |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 422 | Unprocessable Entity | Validation error |
| 500 | Internal Server Error | Server error |

## Error Response Format

```json
{
  "detail": "Error message describing what went wrong",
  "status": 400,
  "error_code": "ERROR_CODE_NAME"
}
```

## Rate Limiting

Currently no rate limiting is enforced, but may be added in future versions.

## Pagination

For endpoints that return lists, use `skip` and `limit` parameters:

```
GET /api/datasets/?skip=20&limit=10
```

Returns records 21-30 (assuming 1-based indexing converted to 0-based).

## Common Query Patterns

### Get user's datasets
```bash
curl -H "Authorization: Bearer <token>" \
  "http://localhost:8000/api/datasets/?limit=100"
```

### Get recent validations
```bash
curl -H "Authorization: Bearer <token>" \
  "http://localhost:8000/api/validations/?skip=0&limit=20"
```

### Get validations for specific dataset
```bash
curl -H "Authorization: Bearer <token>" \
  "http://localhost:8000/api/validations/?dataset_id=1&limit=50"
```

## Changelog

### Version 1.0.0
- Initial API release
- JWT authentication
- Dataset management
- Validation tracking

---

For more information, visit the interactive API documentation at: `/docs`
