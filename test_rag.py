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