# 🤖 AI Agent Knowledge Management System

A complete solution for **managing AI agents** and their corresponding **knowledge bases**, composed of documents like **PDF, Word, Excel, and PowerPoint**.  

Built with modern technologies and designed following **Hexagonal Architecture** for scalability and maintainability.  

---

## 🏗️ Tech Stack

**Frontend**
- ⚛️ React + Next.js 14+
- 🎨 Tailwind CSS + shadcn/ui
- 📊 React Query (TanStack Query)
- 🌐 Axios HTTP client

**Backend**
- 🐍 Python 3.12
- ⚡ FastAPI
- 🏗️ Hexagonal Architecture
- 🧪 Pytest + Coverage

**Storage & Database**
- ☁️ AWS S3 (file storage)
- 🍃 MongoDB Atlas (metadata & documents)
- 🔐 Presigned URLs for secure downloads

---

## 🎯 Features

✅ **Agent Management**  
- Create, edit, and delete agents  
- Assign each agent a name and descriptive prompt  

📂 **Knowledge Base Handling**  
- Upload `.PDF`, `.DOCX`, `.XLSX`, `.PPTX` files (max 10MB)
- Automatic validation of file types and sizes
- Store documents in dedicated agent folders on AWS S3
- Secure file downloads with presigned URLs

📑 **Data Access**  
- List all agents with document counts  
- View detailed agent info + document links  
- Real-time UI updates with React Query

🗑️ **Cleanup**  
- Delete individual files (both from S3 & MongoDB)  
- Delete agents (removes all related documents automatically)
- Automatic S3 folder cleanup

🎨 **User Experience**
- Drag & drop file uploads
- Loading indicators and progress feedback
- Toast notifications for all operations
- Responsive design for all devices

---

## 🚀 Quick Start

### Prerequisites

- **Docker** (recommended) or Python 3.12+
- **Node.js** 18+ and npm
- **MongoDB Atlas** account
- **AWS S3** bucket with credentials

### 🔧 Environment Setup

1. **Clone the repository:**
```bash
git clone <repository-url>
cd Agents-management
```

2. **Backend Environment:**
```bash
cd backend
cp .env.example .env
# Edit .env with your credentials:
# - MongoDB Atlas connection string
# - AWS S3 bucket name and credentials
# - Other configuration values
```

3. **Frontend Environment:**
```bash
cd frontend
cp .env.local.example .env.local
# Edit .env.local with your backend URL
```

### 🐳 Running with Docker (Recommended)

**Backend:**
```bash
cd backend
docker build -t ai-agents-backend .
docker run -d --name ai-agents -p 8000:8000 --env-file .env ai-agents-backend
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

### 🛠️ Running with Local Development

**Backend:**
```bash
cd backend
pip install -e .
python main.py
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

### 📱 Access the Application

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/api/v1/docs

---

## 🔑 Environment Variables

### Backend (.env)
```env
# Database
MONGODB_CONNECTION_STRING=mongodb+srv://...
DATABASE_NAME=ai_agents_db

# AWS S3
AWS_S3_BUCKET_NAME=your-bucket-name
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=us-east-1

# Application
API_PREFIX=/api/v1
APP_VERSION=1.0.0
ENVIRONMENT=development
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

---

## 🧪 Testing

**Backend Tests:**
```bash
cd backend
pytest --cov=src tests/
```

**Frontend Tests:**
```bash
cd frontend
npm test
```

---

## 📁 Project Structure

```
Agents-management/
├── backend/                    # FastAPI backend
│   ├── src/
│   │   ├── application/       # Use cases & DTOs
│   │   ├── domain/           # Business logic & entities
│   │   ├── infrastructure/   # External services & adapters
│   │   └── shared/          # Utilities & validators
│   ├── tests/               # Test suite
│   ├── Dockerfile
│   └── main.py
├── frontend/                  # Next.js frontend
│   ├── src/
│   │   ├── app/             # Next.js 14+ app router
│   │   ├── components/      # React components
│   │   ├── hooks/          # Custom React hooks
│   │   ├── lib/            # Utilities & validations
│   │   └── services/       # API client
│   └── package.json
└── README.md
```

---

## 🔄 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/agents` | List all agents |
| `POST` | `/api/v1/agents` | Create new agent |
| `GET` | `/api/v1/agents/{id}` | Get agent details |
| `PUT` | `/api/v1/agents/{id}` | Update agent |
| `DELETE` | `/api/v1/agents/{id}` | Delete agent |
| `GET` | `/api/v1/documents/` | List documents |
| `POST` | `/api/v1/documents/upload` | Upload document |
| `GET` | `/api/v1/documents/{id}/download` | Download document |
| `DELETE` | `/api/v1/documents/{id}` | Delete document |

---

## 🛡️ Security Features

- **Input Validation:** File type, size, and content validation
- **Secure Downloads:** Presigned URLs with 1-hour expiration
- **Error Handling:** Comprehensive error messages and logging
- **CORS:** Configured for cross-origin requests
- **Async Operations:** Non-blocking I/O for better performance

---
