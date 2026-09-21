from app.rag import build_knowledge_base


count = build_knowledge_base()

print(f"Knowledge base built successfully.")
print(f"Stored chunks: {count}")