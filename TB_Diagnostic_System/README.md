# TB Diagnostic System

A comprehensive tuberculosis diagnostic system with ML-based predictions, patient management, and alerts.

## Project Structure

```
TB_Diagnostic_System/
├── backend/          # Flask API + ML Model
│   ├── models/       # Database models + training code
│   ├── app.py        # Main API server
│   ├── requirements.txt
│   └── .env          # Configuration
└── frontend/         # Nuxt 3 + Tailwind UI
    ├── app.vue
    └── package.json
```

## Features

- **Multi-database support** (SQLite, MySQL, PostgreSQL)
- **Symptom analysis** with risk assessment
- **Test result evaluation** with confidence scores
- **ML-based predictions** for drug resistance
- **Comprehensive treatment recommendations**
- **Patient management system**
- **In-app and email alerts** for high-risk cases
- **Dark/light mode UI**

## Setup

### Backend

1. Install dependencies:
```bash
cd backend
pip install -r requirements.txt
```

2. Configure `.env` (optional, defaults to SQLite):
```env
DATABASE_TYPE=sqlite  # or mysql/postgresql
```

3. Run the server:
```bash
python app.py
```

### Frontend

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Run development server:
```bash
npm run dev
```

## API Endpoints

- `POST /api/diagnose` - Analyze patient and get diagnosis
- `GET/POST /api/patients` - Patient management
- `GET /api/diagnoses` - View saved diagnoses
- `GET /api/alerts` - View alerts
- `PUT /api/alerts/:id/read` - Mark alert as read
- `POST /api/train-model` - Train ML model from database

## Database Configuration

### SQLite (Default)
No extra config needed.

### MySQL
```env
DATABASE_TYPE=mysql
DB_USER=root
DB_PASSWORD=yourpassword
DB_HOST=localhost
DB_PORT=3306
DB_NAME=tb_diagnostic
```

### PostgreSQL
```env
DATABASE_TYPE=postgresql
DB_USER=postgres
DB_PASSWORD=yourpassword
DB_HOST=localhost
DB_PORT=5432
DB_NAME=tb_diagnostic
```
