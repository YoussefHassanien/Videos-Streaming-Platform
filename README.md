# Youverse Video Streaming Platform

A secure, DRM-protected video streaming platform built with FastAPI, PostgreSQL, and Mux integration. This platform enables instructors to upload and manage video courses while providing students with secure access to subscribed content.

## 🎯 Project Overview

### Purpose

This project is a backend service designed for Youverse Learning's internship assessment. It demonstrates the implementation of a production-ready video streaming platform with the following core capabilities:

- **DRM-Protected Video Upload**: Single and batch video uploads using Mux DRM platform
- **Course Management**: Organize videos into course playlists with comprehensive metadata
- **Secure Streaming**: Serve DRM-protected video links only to authenticated and authorized users
- **Access Control**: Subscription-based content access with role-based authentication

### Key Features

🔐 **Security First**

- JWT-based authentication with role-based access control
- Rate limiting on all API endpoints
- DRM-protected video streams via Mux
- Subscription-based content access control

📹 **Video Management**

- Single video upload for individual lectures
- Batch upload (up to 2 videos simultaneously)
- Automatic video processing and streaming-ready link generation
- Comprehensive metadata storage (title, description, duration, category, subcategory)

👥 **User Management**

- Instructor role: Create courses, upload videos, manage content
- Student role: Subscribe to courses, access video content
- Secure user registration and authentication

📚 **Course Organization**

- Link videos to course playlists
- Paginated course listings
- Instructor-specific course management
- Student subscription management

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI App   │    │   PostgreSQL    │    │   Mux DRM       │
│                 │    │                 │    │                 │
│ • REST APIs     │◄──►│ • User Data     │    │ • Video Storage │
│ • Authentication│    │ • Course Data   │    │ • DRM Protection│
│ • Rate Limiting │    │ • Subscriptions │    │ • Streaming URLs│
│ • Error Handling│    │ • Video Metadata│    │ • Asset Processing│
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Technology Stack

- **Backend Framework**: FastAPI 0.115.14
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Video Platform**: Mux (DRM-enabled video hosting)
- **Authentication**: JWT tokens with python-jose
- **Rate Limiting**: SlowAPI
- **Password Hashing**: Bcrypt
- **Environment Management**: python-dotenv

## 📋 Prerequisites

Before installing this project, ensure you have the following installed on your machine:

### System Requirements

- **Python**: Version 3.11 or higher
- **PostgreSQL**: Version 12 or higher
- **Git**: For cloning the repository

### External Services

- **Mux Account**: Free developer account (https://mux.com/)
  - You'll need: Token ID, Token Secret, Signing Key ID, and Private Key

## 🚀 Installation Guide

### Step 1: Clone the Repository

```bash
# Clone the repository
git clone https://github.com/yourusername/Videos-Streaming-Platform.git

# Navigate to the project directory
cd Videos-Streaming-Platform
```

### Step 2: Set Up Python Virtual Environment

```bash
# Create a virtual environment
python -m venv .venv

# Activate the virtual environment
# On Windows:
.venv\Scripts\activate

# On macOS/Linux:
source .venv/bin/activate
```

### Step 3: Install Dependencies

```bash
# Install all required packages
pip install -r requirements.txt
```

### Step 4: Set Up PostgreSQL Database

#### Option A: Local PostgreSQL Installation

1. **Install PostgreSQL** (if not already installed):

   - Windows: Download from https://www.postgresql.org/download/windows/
   - macOS: `brew install postgresql`
   - Ubuntu: `sudo apt-get install postgresql postgresql-contrib`

2. **Create Database**:

```sql
-- Connect to PostgreSQL as superuser
psql -U postgres

-- Create database
CREATE DATABASE video_streaming_platform;

-- Create user (optional, for security)
CREATE USER youverse_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE video_streaming_platform TO youverse_user;

-- Exit
\q
```

#### Option B: Docker PostgreSQL (Alternative)

```bash
# Run PostgreSQL in Docker
docker run --name postgres-youverse \
  -e POSTGRES_PASSWORD=your_password \
  -e POSTGRES_DB=video_streaming_platform \
  -p 5432:5432 \
  -d postgres:15
```

### Step 5: Configure Environment Variables

1. **Create `.env` file** in the project root:

```bash
# Copy the example environment file
cp .env.example .env
```

2. **Edit `.env` file** with your configuration:

```env
# Application Environment
ENVIRONMENT=development

# Database Configuration
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/video_streaming_platform?sslmode=disable

# JWT Configuration
ACCESS_TOKEN_SECRET_KEY=your_secret_key_here_make_it_very_long_and_secure
ACCESS_TOKEN_EXPIRE_MINUTES=120
ACCESS_TOKEN_ALGORITHM=HS256

# Mux Configuration (Get these from your Mux dashboard)
MUX_TOKEN_ID=your_mux_token_id
MUX_TOKEN_SECRET=your_mux_token_secret
MUX_SIGNING_KEY_ID=your_mux_signing_key_id
MUX_PRIVATE_KEY="your_base64_encoded_private_key"
```

### Step 6: Set Up Mux Account

1. **Create Mux Account**:

   - Go to https://mux.com/
   - Sign up for a free developer account

2. **Get API Credentials**:

   - Navigate to Settings > Access Tokens
   - Create a new token with these permissions:
     - Mux Video: Read, Write
     - Mux Data: Read
   - Copy the Token ID and Secret

3. **Create Signing Keys** (for secure playback):
   - Navigate to Settings > Signing Keys
   - Create a new signing key
   - Download the private key and encode it to base64:

```bash
# On macOS/Linux:
base64 -i your_private_key.pem

# On Windows (PowerShell):
[Convert]::ToBase64String([IO.File]::ReadAllBytes("your_private_key.pem"))
```

### Step 7: Generate JWT Secret Key

```bash
# Generate a secure secret key
python -c "import secrets; print(secrets.token_hex(64))"
```

Copy the output and use it as your `ACCESS_TOKEN_SECRET_KEY` in the `.env` file.

### Step 8: Initialize Database

The application will automatically create database tables on first startup in development mode.

```bash
# Start the application (this will create tables)
uvicorn src.app:app --reload --host 127.0.0.1 --port 8000
```

### Step 9: Verify Installation

1. **Check API Documentation**:

   - Open your browser and go to: http://127.0.0.1:8000/docs
   - You should see the Swagger UI with all API endpoints

2. **Test Health Check**:

```bash
curl http://127.0.0.1:8000/
```

Expected response: `{"message": "Youverse Task APIs"}`

## 🔧 Development Setup

### Running the Application

```bash
# Development mode with auto-reload
uvicorn src.app:app --reload --host 127.0.0.1 --port 8000

# Production mode
uvicorn src.app:app --host 0.0.0.0 --port 8000
```

### Environment Variables Explained

| Variable                      | Description                    | Example                                    |
| ----------------------------- | ------------------------------ | ------------------------------------------ |
| `ENVIRONMENT`                 | Application environment        | `development` or `production`              |
| `DATABASE_URL`                | PostgreSQL connection string   | `postgresql://user:pass@localhost:5432/db` |
| `ACCESS_TOKEN_SECRET_KEY`     | JWT signing secret             | Generated 64-character hex string          |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | JWT token expiration time      | `120` (2 hours)                            |
| `MUX_TOKEN_ID`                | Mux API token identifier       | From Mux dashboard                         |
| `MUX_TOKEN_SECRET`            | Mux API token secret           | From Mux dashboard                         |
| `MUX_SIGNING_KEY_ID`          | Mux signing key identifier     | From Mux dashboard                         |
| `MUX_PRIVATE_KEY`             | Base64 encoded Mux private key | Encoded private key                        |

## 📚 API Documentation

### Authentication Endpoints

#### Register User

```bash
POST /api/v1/auth/register
Content-Type: application/json

{
  "first_name": "John",
  "last_name": "Doe",
  "email": "john@example.com",
  "password": "secure_password123",
  "date_of_birth": "1990-01-01",
  "mobile_number": "+1234567890",
  "role": "instructor"  // or "student"
}
```

#### Login

```bash
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "john@example.com",
  "password": "secure_password123"
}
```

### Instructor Endpoints

#### Create Course

```bash
POST /api/v1/course/
Authorization: Bearer <your_jwt_token>
Content-Type: application/json

{
  "title": "Python Programming",
  "description": "Learn Python from basics to advanced"
}
```

#### Upload Single Video

```bash
POST /api/v1/course/add-lecture
Authorization: Bearer <your_jwt_token>
Content-Type: multipart/form-data

lecture_file: video.mp4
title: "Introduction to Variables"
description: "Learn about Python variables"
category: "Programming"
subcategory: "Basics"
course_id: "course-uuid"
```

#### Batch Upload Videos

```bash
POST /api/v1/course/add-lectures-batch
Authorization: Bearer <your_jwt_token>
Content-Type: multipart/form-data

lectures_files: video1.mp4
lectures_files: video2.mp4
lectures_data: [
  {
    "course_id": "course-uuid-1",
    "title": "Lecture 1",
    "description": "First lecture",
    "category": "Programming",
    "subcategory": "Basics"
  },
  {
    "course_id": "course-uuid-2",
    "title": "Lecture 2",
    "description": "Second lecture",
    "category": "Programming",
    "subcategory": "Advanced"
  }
]
```

### Student Endpoints

#### Subscribe to Course

```bash
POST /api/v1/subscribe/
Authorization: Bearer <your_jwt_token>
Content-Type: application/json

{
  "course_id": "course-uuid"
}
```

#### Get Subscribed Courses

```bash
GET /api/v1/subscribe/my-courses?page=1&size=10
Authorization: Bearer <your_jwt_token>
```

#### Get Course Lectures

```bash
GET /api/v1/subscribe/my-courses/{course_id}/lectures
Authorization: Bearer <your_jwt_token>
```

### Public Endpoints

#### Get All Courses

```bash
GET /api/v1/course/all?page=1&size=10
```

## 🛡️ Security Features

### Rate Limiting

- Authentication endpoints: 5-10 requests per minute
- General endpoints: 50 requests per minute
- Automatic IP-based blocking for abuse prevention

### Access Control

- JWT-based authentication
- Role-based authorization (INSTRUCTOR/STUDENT)
- Subscription-based content access
- DRM-protected video streams

### Data Protection

- Bcrypt password hashing
- Environment variable configuration
- SQL injection prevention via SQLAlchemy ORM
- Input validation with Pydantic

## 🗄️ Database Schema

### Users Table

- `id`: Primary key (UUID)
- `first_name`, `last_name`: User names
- `email`: Unique email address
- `password`: Bcrypt hashed password
- `date_of_birth`: User's birth date
- `mobile_number`: Unique phone number
- `role`: INSTRUCTOR or STUDENT
- `created_at`, `updated_at`: Timestamps

### Courses Table

- `id`: Primary key (UUID)
- `title`: Course title
- `description`: Course description
- `duration`: Total course duration (auto-calculated)
- `lectures_count`: Number of lectures (auto-calculated)
- `premium`: Premium course flag
- `instructor_id`: Foreign key to users table
- `created_at`, `updated_at`: Timestamps

### Lectures Table

- `id`: Primary key (UUID)
- `title`: Lecture title
- `description`: Lecture description
- `asset_id`: Mux asset identifier
- `playback_id`: Mux playback identifier
- `url`: Streaming URL
- `duration`: Video duration
- `category`, `subcategory`: Content categorization
- `course_id`: Foreign key to courses table
- `created_at`, `updated_at`: Timestamps

### Subscriptions Table

- `id`: Primary key (UUID)
- `student_id`: Foreign key to users table
- `course_id`: Foreign key to courses table
- `created_at`, `updated_at`: Timestamps
- Unique constraint on (student_id, course_id)

## 🔍 Troubleshooting

### Common Issues

#### Database Connection Error

```
sqlalchemy.exc.OperationalError: could not connect to server
```

**Solution**: Verify PostgreSQL is running and DATABASE_URL is correct.

#### Mux API Error

```
mux_python.exceptions.APIError: 401 Unauthorized
```

**Solution**: Check your Mux credentials in the `.env` file.

#### JWT Token Error

```
{"detail": "Could not validate credentials"}
```

**Solution**: Ensure you're including the Bearer token in the Authorization header.

#### Rate Limit Exceeded

```
{"detail": "Rate limit exceeded: 50 per 1 minute"}
```

**Solution**: Wait for the rate limit window to reset or adjust the limits in the code.

### Debug Mode

Enable debug logging by setting the environment variable:

```bash
export PYTHONPATH="${PYTHONPATH}:/path/to/your/project"
export LOG_LEVEL=DEBUG
```

## 🚀 Deployment

### Production Considerations

1. **Environment Variables**:

   - Use a secure secret management system
   - Set `ENVIRONMENT=production`
   - Use strong, unique passwords

2. **Database**:

   - Use managed PostgreSQL service (AWS RDS, Google Cloud SQL)
   - Enable SSL connections
   - Regular backups

3. **Security**:
   - Use HTTPS in production
   - Implement proper CORS settings
   - Consider using a reverse proxy (nginx)

### Docker Deployment

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ ./src/
COPY .env .

EXPOSE 8000
CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
# Build and run
docker build -t youverse-api .
docker run -p 8000:8000 youverse-api
```

## 🤝 Contributing

This project was developed as part of Youverse Learning's internship assessment. The codebase demonstrates:

- Clean architecture with modular design
- Comprehensive error handling
- Security best practices
- Scalable database design
- Production-ready code quality

## 📄 License

This project is developed for educational and assessment purposes.

## 📞 Support

For questions or issues related to this implementation, please refer to the comprehensive API documentation available at `/docs` when the application is running.

---

**Note**: This README provides a complete guide for setting up and running the Youverse Video Streaming Platform. Follow each step carefully to ensure proper installation and configuration.
