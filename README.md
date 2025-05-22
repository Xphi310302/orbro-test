# Orbro Test Application

A full-stack application with FastAPI backend and React TypeScript frontend.

## Prerequisites

- Docker and Docker Compose
- Git

## Quick Start with Docker

The easiest way to run the application is using Docker Compose:

```bash
# Clone the repository
git clone https://github.com/Xphi310302/orbro-test.git
cd orbro-test

# Start the application
docker compose up --build
```

The application will be available at:
- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## Manual Setup

### Backend Setup

```bash
cd backend

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the backend
python main.py
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run the development server
npm run dev
```

## Project Structure

```
.
├── backend/                 # FastAPI backend
│   ├── main.py             # Main application entry
│   ├── db.py               # Database operations
│   ├── detection.py        # Core business logic
│   └── requirements.txt    # Python dependencies
│
├── frontend/               # React TypeScript frontend
│   ├── src/               # Source files
│   ├── public/            # Static files
│   └── package.json       # Node.js dependencies
│
└── docker-compose.yml     # Docker composition file
```

## Development

- Backend API documentation is available at http://localhost:8000/docs
- Frontend development server includes hot-reload
- Backend development server includes auto-reload

## Database

The application uses SQLite as its database. The database file is created automatically when the application starts.

## File Storage

Uploaded files are stored in:
- `backend/uploads/`: For uploaded files
- `backend/results/`: For processed results

## Notes
- Both services are containerized for consistent development and deployment environments