# Modular Test 01

A modern full-stack application built with Django REST Framework and Vue.js, organized as a mono-repo.

## 🏗️ Project Structure

```
modular-test-01/
├── backend/           # Django REST API
│   ├── config/       # Django settings and configuration
│   ├── apps/         # Django applications
│   └── tests/        # Backend tests
├── frontend/         # Vue.js SPA
│   ├── src/          # Vue source code
│   ├── public/       # Static assets
│   └── tests/        # Frontend tests
├── docs/             # Documentation
├── .github/          # GitHub workflows and templates
└── docker-compose.yml # Local development environment
```

## 🚀 Tech Stack

### Backend
- **Framework:** Django 5.1.3 + Django REST Framework
- **Database:** PostgreSQL 16
- **Cache/Queue:** Redis 7 + Celery
- **Storage:** MinIO (S3-compatible)
- **Testing:** pytest, factory_boy
- **Type Checking:** mypy
- **Code Quality:** black, isort, ruff

### Frontend
- **Framework:** Vue 3.5 + TypeScript
- **UI Library:** Vuetify 3
- **State Management:** Pinia
- **Build Tool:** Vite
- **Testing:** Vitest
- **Code Quality:** ESLint, Prettier

### Infrastructure
- **Containerization:** Docker & Docker Compose
- **Email Testing:** Mailpit
- **API Documentation:** drf-spectacular

## 🛠️ Prerequisites

### System Requirements
- Python 3.12+
- Node.js 20 LTS (or 22)
- Git
- Docker + Docker Compose

### OS Libraries (for PDF/Image processing)
- Poppler
- Cairo
- Pango
- GDK-Pixbuf
- libffi

## ⚡ Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/modular-test-01.git
cd modular-test-01
```

### 2. Setup Git Hooks & Branch Protection
```bash
# Install pre-commit hooks
pip install pre-commit
pre-commit install

# Setup custom branch protection hooks
# Windows: setup-hooks.bat
# Unix/Mac: ./setup-hooks.sh

# Configure branch protection (in .env)
# ALLOW_DIRECT_PUSH_TO_MAIN=true  # Allow direct pushes (development)
# ALLOW_DIRECT_PUSH_TO_MAIN=false # Block direct pushes (production)
```

### 3. Start Docker Services
```bash
docker-compose up -d
```

This starts:
- PostgreSQL 16 (with pg_trgm extension)
- Redis 7
- MinIO (S3-compatible storage)
- Mailpit (email testing)

### 4. Backend Setup
```bash
cd backend
python -m venv venv
# Windows: venv\Scripts\activate
# Unix/macOS: source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### 5. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### 6. Celery Worker (optional)
```bash
cd backend
celery -A config worker -l info
```

## 🌐 Development URLs

- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/api/docs/
- **Django Admin:** http://localhost:8000/admin/
- **MinIO Console:** http://localhost:9001
- **Mailpit UI:** http://localhost:8025

## 📝 Development Workflow

### Backend Commands
```bash
cd backend
python manage.py runserver         # Start Django dev server
python manage.py test              # Run Django tests
pytest                            # Run tests with pytest
black .                          # Format code
isort .                          # Sort imports
ruff check .                     # Lint code
mypy .                          # Type check
pre-commit run --all-files       # Run all pre-commit hooks
```

### Frontend Commands
```bash
cd frontend
npm run dev                      # Start dev server
npm run build                    # Build for production
npm run lint                     # Lint and fix code
npm run format                   # Format code with Prettier
npm run test                     # Run tests
npm run test:ui                  # Run tests with UI
npm run test:coverage            # Run tests with coverage
npm run type-check              # Type check
```

### Docker Commands
```bash
docker-compose up -d             # Start all services
docker-compose down              # Stop all services
docker-compose logs -f [service] # View logs
docker-compose ps               # List running services
```

## 🧪 Testing

### Running Tests
```bash
# Backend tests
cd backend && pytest

# Frontend tests
cd frontend && npm run test

# With coverage
cd backend && pytest --cov
cd frontend && npm run test:coverage
```

## 📦 Building for Production

### Backend
```bash
cd backend
python manage.py collectstatic --noinput
gunicorn config.wsgi:application
```

### Frontend
```bash
cd frontend
npm run build
# Output in dist/ directory
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Team

- [Your Name] - Initial work

## 🙏 Acknowledgments

- Django & Django REST Framework community
- Vue.js ecosystem contributors
- All open source package maintainers