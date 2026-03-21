# Real-Time AI Chat Application

A full-stack real-time chat application with AI integration built with React, FastAPI, Socket.IO, and SQLite.

## Features

- Real-time messaging with Socket.IO
- User authentication (JWT)
- AI chatbot integration (OpenAI GPT)
- Persistent storage with SQLite
- Typing indicators
- Online status indicators
- Modern UI with Tailwind CSS

## Tech Stack

**Frontend:**
- React + Vite
- Tailwind CSS
- Socket.IO Client
- React Router

**Backend:**
- FastAPI (Python)
- Socket.IO Server
- SQLite Database
- JWT Authentication
- OpenAI API

## Prerequisites

- Python 3.9+
- Node.js 18+
- OpenAI API Key (optional, for AI chatbot)

## Project Structure

```
Real-Time-AI-Chat-App/
├── backend/
│   ├── main.py           # FastAPI + Socket.IO server
│   ├── database.py       # SQLite database connection
│   ├── sqlite_db.py      # SQLite database wrapper
│   ├── config.py         # Environment configuration
│   ├── models/           # Pydantic models
│   ├── routes/           # API endpoints
│   ├── services/          # AI service
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── pages/        # Login, Signup, Chat
│   │   ├── components/    # UI components
│   │   ├── services/      # API & Socket clients
│   │   └── context/       # Auth context
│   └── package.json
└── README.md
```

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/sanjay26052003/Real-Time-AI-Chat-App.git
cd Real-Time-AI-Chat-App
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Frontend Setup

```bash
cd frontend
npm install
```

### 4. Configure Environment (Optional)

Edit `backend/.env` to configure settings:

```env
MONGO_URI=mongodb://localhost:27017  # Not used anymore (SQLite is default)
JWT_SECRET=your-secret-key-here
OPENAI_API_KEY=your-openai-api-key  # Optional, for AI chatbot
```

**Note:** The app uses SQLite by default, so MongoDB is not required.

## Running the Application

### 1. Start the Backend Server

```bash
cd backend
venv\Scripts\activate
uvicorn main:app --host 0.0.0.0 --port 8000
```

Backend will run at: http://localhost:8000

### 2. Start the Frontend (in a new terminal)

```bash
cd frontend
npm run dev
```

Frontend will run at: http://localhost:5173

### 3. Open in Browser

Navigate to http://localhost:5173

## Usage

### Creating an Account

1. Click "Sign up" on the login page
2. Enter username, email, and password
3. Click "Create Account"

### Chatting with Other Users

1. Register two different accounts
2. Login with one account
3. You'll see other users in the sidebar
4. Click on a user to start chatting

### Chatting with AI Bot

1. Login to your account
2. Select "AI Bot" from the sidebar
3. Send any message to chat with AI

## API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register new user |
| POST | `/auth/login` | Login and get JWT token |
| GET | `/auth/me` | Get current user info |
| GET | `/auth/users` | Get all users |

### Chat

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/chat/messages/{user_id}` | Get chat history with user |
| POST | `/chat/messages` | Send a message |

### WebSocket Events

- `connect` - Connect with JWT token
- `send_message` - Send a message
- `typing` - Send typing indicator
- `message` - Receive a message
- `status` - User online/offline status

## Database

The application uses SQLite for data persistence. The database file is located at:

```
backend/chat.db
```

This file is automatically created on first run.

## Troubleshooting

### Socket.IO Connection Issues

If you see WebSocket connection errors:
1. Make sure the backend server is running on port 8000
2. Check that no firewall is blocking the connection

### Database Errors

If you encounter database errors:
1. Delete `backend/chat.db` to reset the database
2. Restart the backend server

### AI Bot Not Working

To use the AI chatbot:
1. Get an API key from https://platform.openai.com/
2. Add it to `backend/.env` as `OPENAI_API_KEY`
3. Restart the backend server

## Development

### Running Tests

```bash
# Backend
cd backend
pytest

# Frontend
cd frontend
npm test
```

### Building for Production

```bash
cd frontend
npm run build
```

## License

MIT License
