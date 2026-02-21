# Multi-Agent Trading Signal Generation System

A production-grade multi-agent AI system that generates 15-30 minute trading signals by analyzing financial instruments through four analytical pillars: Fundamental, Economic, Technical, and Social Sentiment analysis.

## Features

- **4 Analysis Agents**: Fundamental, Economic, Technical, and Sentiment analysis
- **Real-time Signal Generation**: Generate trading signals in <90 seconds
- **Modern Frontend**: Next.js 14 with TypeScript and Tailwind CSS
- **WebSocket Support**: Real-time signal updates
- **Authentication**: JWT-based user authentication
- **Safety Validators**: Comprehensive signal validation and guardrails

## Architecture

```
Frontend (Next.js) → Backend (FastAPI) → CrewAI Orchestrator → 4 Analysis Agents
                                                              ↓
                                                    Data Sources (Alpha Vantage, Finnhub, FRED)
```

## Tech Stack

### Backend
- Python 3.11+
- FastAPI
- CrewAI (Multi-agent orchestration)
- OpenAI GPT-4o-mini
- Redis (Caching)
- SQLite/PostgreSQL (Database)

### Frontend
- Next.js 14 (App Router)
- TypeScript
- Tailwind CSS + Shadcn/ui
- Socket.io (WebSocket)
- Zustand (State management)

## Setup

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file from `.env.example`:
```bash
cp .env.example .env
```

5. Add your API keys to `.env`:
- `OPENAI_API_KEY`
- `ALPHA_VANTAGE_KEY`
- `FINNHUB_KEY`

6. Start Redis (if not using Docker):
```bash
redis-server
```

7. Run the backend:
```bash
uvicorn src.main:app --reload
```

Backend will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create `.env.local` file:
```bash
cp .env.local.example .env.local
```

4. Update `.env.local` with backend URL:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

5. Run the frontend:
```bash
npm run dev
```

Frontend will be available at `http://localhost:3000`

## Docker Setup

### Backend + Redis
```bash
cd backend
docker-compose up -d
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login user

### Signals
- `POST /api/v1/signal` - Generate trading signal
- `GET /api/v1/signals` - Get signal history
- `GET /api/v1/signals/{id}` - Get specific signal

### WebSocket
- `WS /ws/` - Real-time signal updates

## Usage

1. Register/Login at the frontend
2. Navigate to Dashboard
3. Enter an instrument (e.g., "AAPL", "Apple", "EURUSD", "Gold")
4. Click "Generate Signal"
5. View the complete analysis from all 4 agents

## Project Structure

```
.
├── backend/
│   ├── src/
│   │   ├── agents/          # CrewAI agents
│   │   ├── analyzers/       # Analysis logic
│   │   ├── data/            # API clients
│   │   ├── models/          # Pydantic models
│   │   ├── processors/      # Input processing
│   │   ├── routes/          # API routes
│   │   ├── synthesis/       # Decision synthesis
│   │   └── validators/     # Safety validators
│   └── requirements.txt
├── frontend/
│   ├── app/                 # Next.js app router
│   ├── components/          # React components
│   ├── lib/                 # Utilities
│   └── types/               # TypeScript types
└── README.md
```

## Development

### Backend Testing
```bash
cd backend
pytest
```

### Frontend Linting
```bash
cd frontend
npm run lint
```

## License

This project is for educational and demonstration purposes.

## Disclaimer

This system is for informational purposes only. Trading signals are not financial advice. Always do your own research and consult with a financial advisor before making trading decisions.
