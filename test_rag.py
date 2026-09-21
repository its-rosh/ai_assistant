from app.rag import answer_question


result = answer_question(
    "What is the customer compensation policy?"
)

print("\nANSWER:")
print(result["answer"])

print("\nSOURCES:")
for source in result["sources"]:
    print(source)

### now we have 
"""PDFs
    ↓
pypdf extraction
    ↓
279 chunks
    ↓
MiniLM embeddings
    ↓
ChromaDB
    ↓
semantic retrieval
    ↓
5 relevant chunks
    ↓
context
    ↓
OpenRouter
    ↓
answer + sources"""

from app.rag import store_memory, retrieve_memories


store_memory(
    user_message="My favorite programming language is Python.",
    assistant_message="I'll remember that you prefer Python.",
    message_id="test-memory-1"
)


memories = retrieve_memories(
    "What programming language do I like?"
)


for memory in memories:
    print("=" * 60)
    print(memory)