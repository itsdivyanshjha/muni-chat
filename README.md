# Municipal Chat App

A modern web application that provides AI-powered insights and analytics for municipal datasets through natural language queries.

## Project Overview

This application allows users to ask questions about municipal data in plain English and receive intelligent responses with data visualizations. It features a React frontend with a FastAPI backend that processes natural language queries and generates insights from municipal datasets.

## Architecture

- **Frontend**: React + TypeScript + Vite + Tailwind CSS + shadcn/ui
- **Backend**: FastAPI + PostgreSQL + Alembic
- **AI**: OpenRouter API integration for natural language processing
- **Data**: Star schema database design for municipal indicators
- **Containerization**: Docker and Docker Compose ready

## File Structure

```
muni-chat/
├── src/                    # React frontend source code
├── backend/               # FastAPI backend application
├── public/                # Static assets
├── package.json           # Frontend dependencies
├── docker-compose.yml     # Docker services configuration
└── README.md             # This file
```

## Quick Setup

### Prerequisites

- Node.js 18+ and npm
- Python 3.8+ and pip
- Docker and Docker Compose
- OpenRouter API key

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Set up environment:**
   ```bash
   cp env.example .env
   # Edit .env and add your OPENROUTER_API_KEY
   ```

3. **Start services:**
   ```bash
   docker-compose up -d
   ```

4. **Run migrations:**
   ```bash
   pip install -r requirements.txt
   alembic upgrade head
   python seed_data.py
   ```

### Frontend Setup

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Start development server:**
   ```bash
   npm run dev
   ```

3. **Build for production:**
   ```bash
   npm run build
   ```

## Running the Application

- **Backend**: http://localhost:8080
- **Frontend**: http://localhost:8081
- **Database**: PostgreSQL on port 5432

## Docker

Use Docker Compose for easy setup:

```bash
docker-compose up -d
```

This starts all services including PostgreSQL database and FastAPI backend.

## API Endpoints

- `POST /api/insights` - Generate insights from natural language
- `GET /api/schema` - Get database schema
- `GET /api/datasets` - List available datasets
- `GET /healthz` - Health check

## Development

- Backend development server: `uvicorn app:app --reload --host 0.0.0.0 --port 8080`
- Frontend development server: `npm run dev`
- Database migrations: `alembic upgrade head`
