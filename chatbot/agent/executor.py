import json
from chatbot.rag.llm import client
from . import tools

# SCHEMAS DÙNG CHUNG
# Tool RAG: Dùng chung cho cả User và Admin để hỏi đáp sản phẩm
TOOL_RAG = {
    "type": "function",
    "function": {
        "name": "search_product_knowledge",
        "description": "Dùng để tra cứu thông tin chi tiết, cấu hình, mô tả, mức độ đánh giá của sản phẩm khi người dùng hỏi về sản phẩm.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Câu hỏi hoặc từ khóa về sản phẩm cần tìm"}
            },
            "required": ["query"]
        }
    }
}
TOOL_ADMIN_GET_ORDER_DETAIL = {
    "type": "function",
    "function": {
        "name": "admin_get_order_details",
        "description": "DÀNH RIÊNG CHO ADMIN: Dùng để tra cứu chi tiết thông tin, khách hàng mua, địa chỉ, trạng thái và danh sách sản phẩm của một đơn hàng cụ thể theo mã ID đơn (ví dụ: 'chi tiết đơn #15', 'đơn hàng 12 có những gì').",
        "parameters": {
            "type": "object",
            "properties": {
                "order_id": {
                    "type": "string", 
                    "description": "Mã ID của đơn hàng cần tra cứu (trích xuất dạng số nguyên từ câu hỏi của Admin)."
                }
            },
            "required": ["order_id"]
        }
    }
}

# SCHEMAS CHO USER
USER_TOOLS_SCHEMA = [
    TOOL_RAG,
    {
        "type": "function",
        "function": {
            "name": "get_my_order_status",
            "description": "Tra cứu trạng thái đơn hàng của người dùng. Dùng khi khách hỏi 'đơn hàng của tôi', 'đơn hàng ngày... vận chuyển chưa', v.v.",
            "parameters": {
                "type": "object",
                "properties": {
                    "date_str": {"type": "string", "description": "Ngày đặt hàng định dạng YYYY-MM-DD nếu khách có nhắc đến. Nếu không nhắc, để trống."}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "filter_products_by_price",
            "description": "Dùng khi user hỏi về điện thoại ở một mức giá, tầm giá hoặc khoảng giá (Ví dụ: 'dưới 10 triệu', 'khoảng 5-7 triệu').",
            "parameters": {
                "type": "object",
                "properties": {
                    "min_price": {"type": "integer", "description": "Giá thấp nhất (VNĐ)."},
                    "max_price": {"type": "integer", "description": "Giá cao nhất (VNĐ)."}
                }
            }
        }
    }
]

# SCHEMAS CHO ADMIN
ADMIN_TOOLS_SCHEMA = [
    TOOL_RAG,
    TOOL_ADMIN_GET_ORDER_DETAIL,
    {"type": "function", "function": {"name": "filter_products_by_price", "description": "Dùng khi user hỏi về điện thoại ở một mức giá, tầm giá hoặc khoảng giá (Ví dụ: 'dưới 10 triệu', 'khoảng 5-7 triệu').", "parameters": {"type": "object", "properties": {"min_price": {"type": "integer", "description": "Giá thấp nhất (VNĐ)."}, "max_price": {"type": "integer", "description": "Giá cao nhất (VNĐ)."}}}}},
    {"type": "function", "function": {"name": "get_product_inventory", "description": "Xem danh sách và giá tất cả sản phẩm"}},
    {"type": "function", "function": {"name": "update_product_detail", "description": "Sửa thông tin sản phẩm", "parameters": {"type": "object", "properties": {"product_id": {"type": "integer"}, "name": {"type": "string"}, "price": {"type": "integer"}}, "required": ["product_id"]}}},
    {"type": "function", "function": {"name": "get_products_by_brand", "description": "Tìm kiếm danh sách sản phẩm theo tên hãng", "parameters": {"type": "object", "properties": {"brand_name": {"type": "string", "description": "Tên hãng"}}, "required": ["brand_name"]}}},
    {"type": "function", "function": {"name": "get_product_sales_ranking", "description": "Lấy danh sách sản phẩm xếp hạng theo số lượng đã bán", "parameters": {"type": "object", "properties": {"sort_order": {"type": "string", "enum": ["desc", "asc"]}}, "required": ["sort_order"]}}},
    {"type": "function", "function": {"name": "get_all_users", "description": "Xem danh sách và trạng thái tất cả người dùng"}},
    {"type": "function", "function": {"name": "update_user_status", "description": "Khóa hoặc mở khóa người dùng", "parameters": {"type": "object", "properties": {"user_id": {"type": "integer"}, "is_active": {"type": "boolean"}}, "required": ["user_id", "is_active"]}}},
    {"type": "function", "function": {"name": "get_recent_orders", "description": "Xem danh sách đơn hàng", "parameters": {"type": "object", "properties": {"status": {"type": "string", "enum": ["Chờ xử lý", "Đang giao", "Đã hoàn thành", "Đã hủy"]}}}}},
    {"type": "function", "function": {"name": "update_order_status", "description": "Cập nhật trạng thái đơn", "parameters": {"type": "object", "properties": {"order_id": {"type": "integer"}, "new_status": {"type": "string", "enum": ["Chờ xử lý", "Đang giao", "Đã hoàn thành", "Đã hủy"]}}, "required": ["order_id", "new_status"]}}},
    {"type": "function", "function": {"name": "get_product_reviews", "description": "Xem đánh giá", "parameters": {"type": "object", "properties": {"rating": {"type": "integer"}}}}},
    {"type": "function", "function": {"name": "reply_to_review", "description": "Phản hồi đánh giá", "parameters": {"type": "object", "properties": {"review_id": {"type": "integer"}, "reply_text": {"type": "string"}}, "required": ["review_id", "reply_text"]}}},
    {"type": "function", "function": {"name": "get_reviews_by_rating_limit", "description": "Lấy đánh giá dưới mức sao", "parameters": {"type": "object", "properties": {"max_rating": {"type": "integer"}}, "required": ["max_rating"]}}},
    {"type": "function", "function": {"name": "get_revenue_by_date", "description": "Doanh thu ngày", "parameters": {"type": "object", "properties": {"date_str": {"type": "string", "description": "BẮT BUỘC định dạng YYYY-MM-DD. Hãy tự động convert từ câu hỏi của user (VD: 'ngày 12/5/2026' -> '2026-05-12')"}}, "required": ["date_str"]}}},
    {"type": "function", "function": {"name": "get_revenue_by_month", "description": "Doanh thu tháng", "parameters": {"type": "object", "properties": {"month_str": {"type": "string", "description": "BẮT BUỘC định dạng YYYY-MM. Hãy tự động convert từ câu hỏi của user (VD: 'tháng 5/2026' -> '2026-05')"}}, "required": ["month_str"]}}},
    {"type": "function", "function": {"name": "get_revenue_by_year", "description": "Doanh thu năm", "parameters": {"type": "object", "properties": {"year_str": {"type": "string", "description": "BẮT BUỘC định dạng YYYY."}}, "required": ["year_str"]}}},
    {"type": "function", "function": {"name": "get_orders_by_date", "description": "Đơn hàng theo ngày", "parameters": {"type": "object", "properties": {"date_str": {"type": "string", "description": "BẮT BUỘC định dạng YYYY-MM-DD. Hãy tự convert (VD: 15/10/2023 -> 2023-10-15)"}}, "required": ["date_str"]}}},
    {"type": "function", "function": {"name": "get_orders_by_month", "description": "Đơn hàng theo tháng", "parameters": {"type": "object", "properties": {"month_str": {"type": "string", "description": "BẮT BUỘC định dạng YYYY-MM. Hãy tự convert (VD: tháng 10/2023 -> 2023-10)"}}, "required": ["month_str"]}}},
    {"type": "function", "function": {"name": "get_orders_by_year", "description": "Đơn hàng theo năm", "parameters": {"type": "object", "properties": {"year_str": {"type": "string", "description": "BẮT BUỘC định dạng YYYY."}}, "required": ["year_str"]}}}
]

# HÀM CHẠY AGENT CHUNG
def run_agent(user_input, user, role="user"):
    try:
        # Cấu hình Role
        if role == "admin":
            tools_schema = ADMIN_TOOLS_SCHEMA
            sys_prompt = "Bạn là Trợ lý Quản trị viên cấp cao. Hãy dùng công cụ phù hợp để lấy dữ liệu, sau đó tóm tắt và trả lời Admin một cách chính xác, chuyên nghiệp."
        else:
            tools_schema = USER_TOOLS_SCHEMA
            sys_prompt = "Bạn là nhân viên CSKH thân thiện của cửa hàng. Hãy dùng công cụ RAG để tra cứu thông tin sản phẩm, hoặc dùng công cụ kiểm tra đơn hàng nếu khách hỏi. Luôn trả lời tự nhiên, lịch sự và ngắn gọn."

        messages = [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": user_input}
        ]

        # Gọi AI để quyết định có dùng Tool không
        response = client.chat.completions.create(
            model="gemini-2.5-flash",
            messages=messages,
            tools=tools_schema,
            tool_choice="auto"
        )
        
        msg = response.choices[0].message
        
        # Nếu AI trả lời luôn (không dùng tool)
        if not msg.tool_calls:
            return msg.content

        # Nếu AI quyết định dùng Tool
        tool_results = []
        for tool_call in msg.tool_calls:
            func_name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)
            
            # Lấy hàm thực tế từ file tools.py
            func = getattr(tools, func_name)
            
            # Hàm tra cứu cá nhân cần truyền vào object user
            if func_name == "get_my_order_status":
                result = func(user=user, **args)
            else:
                result = func(**args)
                
            tool_results.append(str(result))

        # Truyền kết quả lấy được từ DB lại cho AI để tạo văn bản tự nhiên
        final_context = "\n".join(tool_results)
        
        # Ghi lại lịch sử 
        messages.append(msg) 
        messages.append({
            "role": "user", 
            "content": f"Dữ liệu hệ thống trả về:\n{final_context}\n\nDựa vào đó, hãy trả lời câu hỏi ban đầu của tôi."
        })

        final_response = client.chat.completions.create(
            model="gemini-2.5-flash",
            messages=messages
        )

        return final_response.choices[0].message.content

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return f"Lỗi thực thi Agent: {str(e)}"