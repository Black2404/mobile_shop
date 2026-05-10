from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from .agent.executor import run_agent

# USER CHAT
@api_view(["POST"])
@permission_classes([AllowAny])
def chat(request):
    try:
        question = request.data.get("message", "").strip()
        if not question:
            return Response({"answer": "Bạn chưa nhập câu hỏi nào cả ^^"}, status=200)

        # Chạy Agent với quyền User. Hệ thống sẽ tự động phân loại 
        answer = run_agent(user_input=question, user=request.user, role="user")
        
        return Response({"answer": answer})

    except Exception as e:
        print(f"LỖI SERVER: {str(e)}") 
        return Response({"answer": "Hệ thống đang bảo trì một chút, bạn thử lại sau nhé!"}, status=500)
    
# ADMIN CHAT
@api_view(["POST"])
@permission_classes([IsAdminUser])
def admin_chat(request):
    try:
        question = request.data.get("message")
        if not question:
            return Response({"answer": "Thiếu message"}, status=400)
            
        # Chạy Agent với quyền Admin. Có thể dùng toàn bộ Tools.
        answer = run_agent(user_input=question, user=request.user, role="admin")
        
        return Response({"answer": answer}) 
        
    except Exception as e:
        return Response({"answer": f"Lỗi View: {str(e)}"}, status=500)