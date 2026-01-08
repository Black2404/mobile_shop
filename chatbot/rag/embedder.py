from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")  # nhanh, nhẹ, free

def embed_text(text: str):
    """Trả về embedding vector dạng list float"""
    return model.encode(text).tolist()
