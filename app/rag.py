"""extract_documents()
        ↓
build_chunks()
        ↓
build_knowledge_base()
        ↓
retrieve()
        ↓
build_context()
        ↓
ask_llm()
        ↓
answer_question()"""

### this handles 
"""retrieval
+
context
+
OpenRouter """

import os
from pathlib import Path

import chromadb
import requests
from dotenv import load_dotenv
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer


load_dotenv()

# Configuration

BASE_DIR = Path(__file__).resolve().parent.parent

PDF_FOLDER = BASE_DIR / "requirement"

CHROMA_PATH = os.getenv(
    "CHROMA_PATH",
    str(BASE_DIR / "data" / "chroma")
)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

MODEL_NAME = os.getenv(
    "OPENROUTER_MODEL",
    "inclusionai/ling-3.0-flash-fin:free"
)

# Embedding model

embedding_model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)

# ChromaDB

chroma_client = chromadb.PersistentClient(
    path=CHROMA_PATH
)

## our chorma bd have two collections --- khowledge base and conversation history  
collection = chroma_client.get_or_create_collection(
    name="knowledge_base",
    metadata={"hnsw:space": "cosine"}
)
memory_collection = chroma_client.get_or_create_collection(
    name="conversation_memory",
    metadata={"hnsw:space": "cosine"}
)


# Chunking

def chunk_text(text, chunk_size=1000, overlap=150):

    chunks = []

    start = 0

    while start < len(text):

        end = start + chunk_size

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start += chunk_size - overlap

    return chunks

# Extract PDF pages

def extract_documents():

    documents = []

    for pdf_path in PDF_FOLDER.glob("*.pdf"):

        reader = PdfReader(pdf_path)

        for page_number, page in enumerate(
            reader.pages,
            start=1
        ):

            text = page.extract_text()

            if text and text.strip():

                documents.append({
                    "text": text.strip(),
                    "source": pdf_path.name,
                    "page": page_number
                })

    return documents

# Build chunks

def build_chunks(documents):

    chunks = []

    for document in documents:

        page_chunks = chunk_text(
            document["text"]
        )

        for chunk_index, chunk in enumerate(
            page_chunks
        ):

            chunks.append({
                "text": chunk,
                "source": document["source"],
                "page": document["page"],
                "chunk": chunk_index
            })

    return chunks

# Build / update knowledge base # Build LLM context

def build_context(
    chunks,
    memories=None,
    recent_messages=None
):

    context_parts = []

    # ---------------------------------
    # Shared knowledge-base context
    # ---------------------------------

    if chunks:

        knowledge_context = "\n\n".join(
            f"""
Source: {chunk["source"]}
Page: {chunk["page"]}

{chunk["text"]}
"""
            for chunk in chunks
        )

        context_parts.append(
            "KNOWLEDGE BASE:\n"
            + knowledge_context
        )

    # ---------------------------------
    # User semantic memory
    # ---------------------------------

    if memories:

        memory_context = "\n\n".join(
            memory["text"]
            for memory in memories
        )

        context_parts.append(
            "USER MEMORY:\n"
            + memory_context
        )

    # ---------------------------------
    # Recent conversation
    # ---------------------------------

    if recent_messages:

        conversation_context = "\n\n".join(
            f'{message["role"].upper()}: '
            f'{message["content"]}'
            for message in recent_messages
        )

        context_parts.append(
            "RECENT CONVERSATION:\n"
            + conversation_context
        )

    return "\n\n====================\n\n".join(
        context_parts
    )


def store_memory(
    user_message,
    assistant_message,
    message_id,
    user_id
):
    memory_text = f"""
User:
{user_message}

Assistant:
{assistant_message}
""".strip()

    embedding = embedding_model.encode(
        [memory_text]
    )[0]

    memory_collection.upsert(
        ids=[str(message_id)],
        documents=[memory_text],
        embeddings=[embedding.tolist()],
        metadatas=[
            {
                "type": "conversation",
                "message_id": str(message_id),
                "user_id": str(user_id),
            }
        ]
    )


## retvive form memory 


def retrieve_memories(
    question,
    user_id,
    top_k=5,
    distance_threshold=0.70
):
    query_embedding = embedding_model.encode(
        [question]
    )[0]

    results = memory_collection.query(
        query_embeddings=[
            query_embedding.tolist()
        ],
        n_results=top_k,
        where={
            "user_id": str(user_id)
        }
    )

    memories = []

    if not results["documents"]:
        return memories

    for i, distance in enumerate(
        results["distances"][0]
    ):

        if distance <= distance_threshold:

            memories.append(
                {
                    "text": results["documents"][0][i],
                    "distance": distance,
                    "message_id":
                        results["metadatas"][0][i][
                            "message_id"
                        ]
                }
            )

    return memories


# Retrieve relevant chunks

def retrieve(
    question,
    top_k=5,
    distance_threshold=0.70
):

    query_embedding = embedding_model.encode(
        [question]
    )[0]

    results = collection.query(
        query_embeddings=[
            query_embedding.tolist()
        ],
        n_results=top_k
    )

    relevant_chunks = []

    if not results["documents"]:
        return relevant_chunks

    for i, distance in enumerate(
        results["distances"][0]
    ):

        if distance <= distance_threshold:

            relevant_chunks.append({
                "text": results["documents"][0][i],
                "source": results["metadatas"][0][i]["source"],
                "page": results["metadatas"][0][i]["page"],
                "distance": distance
            })

    return relevant_chunks

# Ask OpenRouter

def ask_llm(question, context):

    if not OPENROUTER_API_KEY:
        raise RuntimeError(
            "OPENROUTER_API_KEY is not configured."
        )

    prompt = f"""
You are a helpful AI assistant.

Use the information provided in the context to answer
the user's question.

The context may contain:

1. KNOWLEDGE BASE
   Shared information extracted from the application's PDFs.

2. USER MEMORY
   Information remembered from this specific user.

3. RECENT CONVERSATION
   Recent messages from this specific user.

Use USER MEMORY and RECENT CONVERSATION when the
question is personal or conversational.

Use KNOWLEDGE BASE when the question is about the
provided documents or business information.

Do not invent facts that are not supported by the context.

If a question about the knowledge base cannot be
answered from the knowledge-base context, say:

I couldn't find enough information in the knowledge base.

Context:

{context}

Question:

{question}
"""

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",

        headers={
            "Authorization": (
                f"Bearer {OPENROUTER_API_KEY}"
            ),
            "Content-Type": "application/json"
        },

        json={
            "model": MODEL_NAME,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        },

        timeout=60
    )

    response.raise_for_status()

    data = response.json()

    return data["choices"][0]["message"]["content"]


# Complete RAG pipeline

def answer_question(
    question,
    user_id,
    recent_messages=None
):

    # Retrieve shared PDF knowledge
    chunks = retrieve(question)

    # Retrieve this user's memories
    memories = retrieve_memories(
        question,
        user_id
    )

    # If nothing useful was found

    if not chunks and not memories and not recent_messages:

        return {
            "answer": (
                "I couldn't find enough information "
                "in the knowledge base."
            ),
            "sources": []
        }

    # Build combined context

    context = build_context(
        chunks=chunks,
        memories=memories,
        recent_messages=recent_messages
    )

    # Ask OpenRouter

    answer = ask_llm(
        question,
        context
    )

    # Sources

    sources = [
        {
            "source": chunk["source"],
            "page": chunk["page"],
            "distance": chunk["distance"]
        }
        for chunk in chunks
    ]

    return {
        "answer": answer,
        "sources": sources
    }