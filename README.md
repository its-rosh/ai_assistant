AI Assistant — Multi-User RAG + Semantic Memory

A Flask-based AI assistant that combines authentication, PostgreSQL conversation history, ChromaDB semantic memory, PDF-based RAG, and OpenRouter into a user-aware architecture.

Conversation history is user-specific, semantic memory is user-specific, and shared knowledge comes from a controlled knowledge base.

✨ What I Have Achieved

✅ Multiple user accounts

✅ Separate authenticated sessions

✅ Signup and login

✅ Password hashing

✅ Flask-Login session management

✅ Conversations associated with authenticated users

✅ PostgreSQL conversation history

✅ User-specific semantic memories in ChromaDB

✅ Semantic memory retrieval filtered by user_id

✅ User A's memory does not leak into User B's retrieval

✅ Shared PDF knowledge base using RAG

✅ PDF text extraction and chunking

✅ Sentence Transformer embeddings

✅ ChromaDB vector retrieval

✅ Distance-based retrieval filtering

✅ OpenRouter integration

✅ Recent conversation context

✅ Semantic memory + recent conversation + PDF knowledge combined into model context

✅ Automatic storage of completed conversations as semantic memories

✅ Existing chat frontend connected to the authenticated backend

🧠 Project Concept

The assistant uses three different kinds of information.

1. PostgreSQL — Complete Conversation History

PostgreSQL stores the chronological conversation record.

User
 ↓
Message
 ↓
PostgreSQL
 ↓
Complete history

Each conversation message is associated with a user:

user_id
role
content
created_at

2. ChromaDB — Semantic Memory

ChromaDB stores useful conversational information as vector embeddings.

Example:

User:
My favorite programming language is Python.

Assistant:
I'll remember that you prefer Python.

The memory includes metadata such as:

user_id
message_id
type

Retrieval is restricted to the authenticated user's memory:

where={
    "user_id": str(user_id)
}

3. ChromaDB — Shared Knowledge Base

A separate ChromaDB collection stores knowledge extracted from project PDFs.

PDF files
 ↓
pypdf
 ↓
Text extraction
 ↓
Chunking
 ↓
SentenceTransformer
 ↓
Embeddings
 ↓
ChromaDB

Shared knowledge is separated from private conversation memory.

🔐 Multi-User Architecture

Authentication establishes the identity of the current user.

Signup
 ↓
users table
 ↓
Login
 ↓
Flask session
 ↓
current_user.id

The authenticated ID is then used throughout the application.

current_user.id
      │
      ├──────────────► PostgreSQL
      │                User's conversations
      │
      └──────────────► ChromaDB
                       User's semantic memory

The backend obtains the identity from the authenticated Flask session rather than trusting a client-supplied user ID for memory retrieval.

🏗️ Full System Flow

                         USER
                           │
                           ▼
                    Signup / Login
                           │
                           ▼
                  Flask Authentication
                           │
                           ▼
                    current_user.id
                           │
             ┌─────────────┼─────────────┐
             │             │             │
             ▼             ▼             ▼
        PostgreSQL     ChromaDB      ChromaDB
        Conversations  User Memory   Knowledge Base
             │             │             │
             │        user_id filter      │
             └─────────────┼─────────────┘
                           ▼
                   Context Assembly
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
         Recent Chat   User Memory   PDF RAG
              └────────────┼────────────┘
                           ▼
                      OpenRouter
                           │
                           ▼
                        Answer
                           │
                 ┌─────────┴─────────┐
                 ▼                   ▼
            PostgreSQL           ChromaDB
            Save history        Save memory

🔄 RAG Pipeline

PDF
 ↓
pypdf
 ↓
Page extraction
 ↓
Chunking
 ↓
SentenceTransformer
 ↓
Embeddings
 ↓
ChromaDB
 ↓
Question embedding
 ↓
Top-k retrieval
 ↓
Distance threshold
 ↓
Relevant context
 ↓
OpenRouter
 ↓
Answer + sources

The application can return source information such as the document name, page, and retrieval distance.

🧠 Memory Pipeline

User message
     +
Assistant response
     ↓
PostgreSQL
     ↓
store_memory()
     ↓
Create embedding
     ↓
ChromaDB
     ↓
conversation_memory
     ↓
user_id metadata

Later:

Question
   ↓
Embedding
   ↓
ChromaDB semantic search
   ↓
Filter by authenticated user_id
   ↓
Relevant memories
   ↓
Context
   ↓
OpenRouter

🛡️ What Makes This Project Unique

The main architectural idea is that the application does not treat all context as one large memory store.

Instead:

                    Context
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
   PostgreSQL      Chroma Memory   Knowledge Base
   Full history    User-specific  Shared reference

User-specific semantic memory

User A
 ├── Memory A1
 ├── Memory A2
 └── Memory A3

User B
 ├── Memory B1
 └── Memory B2

Retrieval uses the authenticated user's ID, creating a clear user-level isolation boundary.

Structured history + semantic memory

The project separates:

PostgreSQL: complete chronological history

ChromaDB: semantic long-term memory

Knowledge base: shared application knowledge

This separation makes the system easier to extend and maintain.

👥 How Other Developers Can Use It

This architecture can be adapted for:

Customer support

Shared company policies
        +
Customer-specific memory
        +
Authenticated accounts

Internal company assistants

Company knowledge base
        +
Employee-specific context
        +
Conversation history

Educational assistants

Course documents
        +
Student-specific memory
        +
Conversation history

Personal productivity assistants

Personal preferences
        +
Long-term semantic memory
        +
Conversation history

Domain-specific assistants

Replace the PDFs with:

Product manuals

Technical documentation

Company policies

Research papers

Training material

Other controlled reference documents

🚀 How to Use

1. Clone

git clone <your-repository-url>
cd ai-assistant

2. Create a virtual environment

Windows:

python -m venv .venv
.venv\Scriptsctivate

macOS/Linux:

python -m venv .venv
source .venv/bin/activate

3. Install dependencies

pip install -r requirements.txt

4. Configure .env

Example:

OPENROUTER_API_KEY=your_openrouter_api_key
OPENROUTER_MODEL=inclusionai/ling-3.0-flash-fin:free

DATABASE_URL=your_postgresql_connection_string

SECRET_KEY=your_secret_key

CHROMA_PATH=./data/chroma

Never commit real API keys, passwords, or production secrets.

5. Run authentication migration

python -m app.migrate_auth

6. Build the knowledge base

python build_knowledge_base.py

7. Start Flask

python -m app.main

📁 Project Structure

ai-assistant/
│
├── app/
│   ├── main.py
│   ├── auth.py
│   ├── database.py
│   ├── rag.py
│   └── migrate_auth.py
│
├── app/templates/
│   ├── index.html
│   ├── login.html
│   └── signup.html
│
├── data/
│   └── chroma/
│
├── requirement/
│   ├── Code-of-Business.pdf
│   ├── compensation-policy.pdf
│   └── mitc_cc.pdf
│
├── build_knowledge_base.py
├── test_rag.py
├── .env
└── requirements.txt

🗄️ Database Structure

Users

users
├── id
├── email
├── password_hash
└── created_at

Conversations

conversations
├── id
├── role
├── content
├── created_at
└── user_id

🔍 Security and Privacy Design

The current architecture includes:

Authentication-based identity

The backend uses:

current_user.id

for authenticated user context.

User-scoped memory retrieval

Chroma retrieval includes:

where={
    "user_id": str(user_id)
}

Password hashing

Passwords are stored as hashes rather than plaintext passwords.

Shared vs private data separation

Shared knowledge
      ≠
Private semantic memory
      ≠
Private conversation history

This is a strong foundation for privacy-aware multi-user applications.

Production deployments should additionally use HTTPS, secure session-cookie configuration, secret management, database permissions, rate limiting, backups, monitoring, and other operational security controls.

🧪 Multi-User Isolation Test

User A

My favorite programming language is Python.

Then:

What is my favorite programming language?

Expected:

Python

User B

Log in with a different account and ask:

What is my favorite programming language?

User B should not receive User A's semantic memory.

Then User B can establish their own memory:

My favorite programming language is JavaScript.

This tests the core user-scoped memory design.

📈 Future Improvements

Planned areas include:

Admin dashboard

User management

Account disabling

Password reset

Memory inspection

Memory deletion

Memory deduplication

Memory importance scoring

Automatic memory extraction

Conversation summarization

Token-aware context selection

Memory expiration policies

Stronger database constraints

Production session-cookie configuration

Rate limiting

Audit logging

Automated tests

Docker deployment

Render deployment

Production PostgreSQL

Persistent production Chroma strategy

Monitoring and error tracking

🎯 Project Philosophy

The project is built around clear responsibilities:

PostgreSQL
= What happened?

Chroma semantic memory
= What is useful to remember?

Knowledge base
= What does the application know?

Authentication
= Whose information is this?

OpenRouter
= How should the available context be turned into an answer?

The result is a foundation for a multi-user, context-aware AI assistant rather than a single-user chatbot with an undifferentiated memory store.

📜 Current Status

Authentication             ✅
Multiple accounts          ✅
Authenticated sessions     ✅
User-scoped history        ✅
PDF RAG                    ✅
Shared knowledge base      ✅
Semantic memory            ✅
User-scoped memory         ✅
Memory retrieval           ✅
Memory isolation           ✅
Recent conversation        ✅
OpenRouter integration     ✅
Automatic memory storage   ✅

Current milestone: Multi-User RAG + Semantic Memory