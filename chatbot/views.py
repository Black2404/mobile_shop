from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

# from chatbot.rag.embedder import embed_text  <-- XÓA DÒNG NÀY (Không cần dùng)
from chatbot.rag.retriever import search_products
from chatbot.rag.prompt import build_prompt
from chatbot.rag.llm import ask_llm

@api_view(["POST"])
@permission_classes([AllowAny]) # Cho phép tất cả mọi người chat
def chat(request):
    try:
        # 1. Lấy câu hỏi từ người dùng
        question = request.data.get("message")
        
        if not question:
            return Response({"answer": "Bạn chưa nhập câu hỏi nào cả ^^"}, status=200)

        # 2. Tìm kiếm sản phẩm
        # --- QUAN TRỌNG: Truyền thẳng text, KHÔNG embed ở đây ---
        contexts = search_products(question) 

        # 3. Gửi cho AI trả lời
        prompt = build_prompt(contexts, question)
        answer = ask_llm(prompt)

        return Response({"answer": answer})

    except Exception as e:
        print(f"LỖI SERVER: {str(e)}") # Xem lỗi ở màn hình đen (terminal)
        return Response({"answer": "Hệ thống đang bảo trì một chút, bạn thử lại sau nhé!"}, status=500)