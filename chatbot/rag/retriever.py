from django.db import connection
from chatbot.rag.embedder import embed_text

def search_products(query: str, k: int = 5):
    # 1. Mã hóa câu hỏi thành vector ngay tại đây
    query_embedding = embed_text(query)

    with connection.cursor() as cursor:
        # 2. Truy vấn SQL: JOIN giữa bảng vector và bảng products
        cursor.execute("""
            SELECT
                p.id,
                p.name,
                pe.content,  
                pe.embedding <-> %s::vector AS distance
            FROM product_embeddings pe
            JOIN products p ON p.id = pe.product_id
            ORDER BY pe.embedding <-> %s::vector
            LIMIT %s
        """, [query_embedding, query_embedding, k])

        rows = cursor.fetchall()

    return [
        {
            "id": r[0], 
            "name": r[1], 
            "content": r[2], 
            "score": float(r[3])
        }
        for r in rows
    ]