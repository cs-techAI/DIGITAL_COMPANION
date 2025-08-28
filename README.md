# Digital Companion - RAG Chatbot

Multi-user RAG chatbot with document processing, video transcription, and YouTube support.

## 🚀 Quick Deploy

### 1. Setup
```bash
cp .env.example .env
# Edit .env with your GEMINI_API_KEY
```

### 2. Run
```bash
docker-compose up -d
```

Access: http://localhost:8501

## 📋 Demo Login
- Student: `student1` / `student123`  
- Teacher: `teacher1` / `teacher123`
- Parent: `parent1` / `parent123`

## ✨ Features
- Multi-user authentication (student/teacher/parent)
- Document upload (PDF, TXT)
- YouTube transcript processing
- Grounded AI responses with source validation
- Role-based UI themes
- Context caching for performance

## 🛠️ Requirements
- Docker & Docker Compose
- Google Gemini API key