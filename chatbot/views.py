from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from chatbot.rag.retriever import search_products
from chatbot.rag.prompt import build_prompt
from chatbot.rag.llm import ask_llm
from products.models import Product

from rest_framework.permissions import IsAdminUser
from .agent.executor import run_admin_agent

# RAG 

@api_view(["POST"])
@permission_classes([AllowAny]) # Cho phép tất cả mọi người chat
def chat(request):
    try:
        # 1. Lấy câu hỏi từ người dùng
        question = request.data.get("message")
        
        if not question:
            return Response({"answer": "Bạn chưa nhập câu hỏi nào cả ^^"}, status=200)

        # 2. Tìm kiếm sản phẩm
        contexts = search_products(question) 

        total_count = Product.objects.count() 
        store_info = f"Tổng số sản phẩm cửa hàng đang có: {total_count}"

        # 3. Gửi cho AI trả lời
        prompt = build_prompt(contexts, question, info=store_info)
        answer = ask_llm(prompt)

        return Response({"answer": answer})

    except Exception as e:
        print(f"LỖI SERVER: {str(e)}") 
        return Response({"answer": "Hệ thống đang bảo trì một chút, bạn thử lại sau nhé!"}, status=500)
    
# AGENTIC

@api_view(["POST"])
@permission_classes([IsAdminUser])
def admin_chat(request):
    try:
        question = request.data.get("message")
        if not question:
            return Response({"answer": "Thiếu message"}, status=400)
            
        answer = run_admin_agent(question)
        return Response({"answer": answer}) 
        
    except Exception as e:
        return Response({"answer": f"Lỗi View: {str(e)}"}, status=500)