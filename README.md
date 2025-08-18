# 🤖 AI Agent Knowledge Management System

A complete solution for **managing AI agents** and their corresponding **knowledge bases**, composed of documents like **PDF, Word, Excel, and PowerPoint**.  

Built with modern technologies and designed following **Hexagonal Architecture** for scalability and maintainability.  

---

## 🏗️ Tech Stack

**Frontend**
- ⚛️ React  
- 🟧 Nest.js  

**Backend**
- 🐍 Python  
- ⚡ FastAPI  

**Storage & Database**
- 📂 Azure Blob Storage / AWS S3  
- 🍃 MongoDB (agent metadata & vector DB)  

---

## 🎯 Features

✅ **Agent Management**  
- Create, edit, and delete agents  
- Assign each agent a descriptive prompt  

📂 **Knowledge Base Handling**  
- Upload `.PDF`, `.DOCX`, `.XLSX`, `.PPTX` files  
- Automatic validation of file types  
- Store documents in dedicated agent folders on Blob Storage  

📑 **Data Access**  
- List all agents with file counts  
- View detailed agent info + document links  

🗑️ **Cleanup**  
- Delete files (both from storage & DB)  
- Delete agents (removes all related documents automatically)  

---

    B --> D[(Azure Blob Storage)]
    B --> E[(Vector Database)]
