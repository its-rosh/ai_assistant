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

# Build / update knowledge base

def build_knowledge_base():

    documents = extract_documents()

    chunks = build_chunks(documents)

    if not chunks:
        raise RuntimeError(
            "No PDF text was found in the requirement folder."
        )

    texts = [
        chunk["text"]
        for chunk in chunks
    ]

    embeddings = embedding_model.encode(
        texts,
        show_progress_bar=True
    )

    ids = [
        f"{chunk['source']}-"
        f"{chunk['page']}-"
        f"{chunk['chunk']}"
        for chunk in chunks
    ]

    metadatas = [
        {
            "source": chunk["source"],
            "page": chunk["page"],
            "chunk": chunk["chunk"]
        }
        for chunk in chunks
    ]

    collection.upsert(
        ids=ids,
        documents=texts,
        embeddings=embeddings.tolist(),
        metadatas=metadatas
    )

    return collection.count()


def store_memory(
    user_message,
    assistant_message,
    message_id
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
            }
        ]
    )


## retvive form memory 


def retrieve_memories(
    question,
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
        n_results=top_k
    )

    memories = []

    if not results["documents"]:
        return memories

    for i, distance in enumerate(
        results["distances"][0]
    ):
        if distance <= distance_threshold:
            memories.append({
                "text": results["documents"][0][i],
                "distance": distance,
                "message_id": results["metadatas"][0][i][
                    "message_id"
                ]
            })

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


# Build LLM context

def build_context(chunks):

    return "\n\n".join(
        f"""
Source: {chunk["source"]}
Page: {chunk["page"]}

{chunk["text"]}
"""
        for chunk in chunks
    )


# Ask OpenRouter

def ask_llm(question, context):

    if not OPENROUTER_API_KEY:
        raise RuntimeError(
            "OPENROUTER_API_KEY is not configured."
        )

    prompt = f"""
You are a knowledge-base assistant.

Answer the user's question using ONLY the
information provided in the context.

If the context does not contain enough information,
respond exactly:

I couldn't find enough information in the knowledge base.

Do not invent information.

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

def answer_question(question):

    chunks = retrieve(question)

    if not chunks:

        return {
            "answer": (
                "I couldn't find enough information "
                "in the knowledge base."
            ),
            "sources": []
        }

    context = build_context(chunks)

    answer = ask_llm(
        question,
        context
    )

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