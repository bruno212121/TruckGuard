# TruckGuard

Comprehensive fleet management system for trucks.

## 🚀 Getting Started

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd TruckGuard
```

2. Create and activate virtual environment:

**Linux/macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp env-example .env
```

Edit the `.env` file with your configurations (database, JWT secret key, etc.).

### Run the Project

**Linux/macOS:**
```bash
./boot.sh
```

**Or manually:**
```bash
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
python app.py
```

The application will be available at `http://localhost:8000`

### API Documentation

Once the application is running, access the interactive Swagger documentation:

```
http://localhost:8000/docs
```

## 📋 Requirements

- Python 3.8+
- MySQL 5.7+ or SQLite (for local development)

## 🔧 Configuration

Copy `env-example` to `.env` and configure:

- `DATABASE_URL`: MySQL connection URL or configure SQLite
- `JWT_SECRET_KEY`: Secret key for JWT tokens (minimum 256 bits)
- `PORT`: Port where the application will run (default: 8000)
- `API_KEY`: Google Maps API key (optional)
- Email configuration (optional)

## 📚 Resources

- **API Docs**: `http://localhost:8000/docs` (Swagger UI)
- **Tests**: `python test/api/run_tests.py`
- **Reset DB**: `python reset_database.py` ⚠️ (deletes all data)

## 🏗️ Structure

```
TruckGuard/
├── app/              # Main application
│   ├── auth/        # Authentication
│   ├── models/      # Database models
│   ├── resources/   # API endpoints
│   └── config/      # Configurations
├── test/            # Tests
└── app.py           # Entry point
```

## 🔐 Authentication

Most endpoints require JWT authentication:

1. Register a user: `POST /auth/register`
2. Login: `POST /auth/login` (you'll get a token)
3. Use the token in requests: `Authorization: Bearer <token>`

---
