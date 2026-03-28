import json
from chatbot.rag.llm import client
from . import tools

AGENT_TOOLS_SCHEMA = [

    # SẢN PHẨM 

    {"type": "function", "function": {"name": "get_product_inventory", "description": "Xem danh sách và giá tất cả sản phẩm"}},
    {
        "type": "function",
        "function": {
            "name": "update_product_detail",
            "description": "Sửa thông tin sản phẩm",
            "parameters": {
                "type": "object",
                "properties": {"product_id": {"type": "integer"}, "name": {"type": "string"}, "price": {"type": "integer"}},
                "required": ["product_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_products_by_brand",
            "description": "Tìm kiếm danh sách sản phẩm theo tên hãng (thương hiệu)",
            "parameters": {
                "type": "object",
                "properties": {
                    "brand_name": {
                        "type": "string", 
                        "description": "Tên hãng muốn tìm (ví dụ: Apple, Samsung, Dell)"
                    }
                },
                "required": ["brand_name"]
            }
        }
    },

    # NGƯỜI DÙNG

    {"type": "function", "function": {"name": "get_all_users", "description": "Xem danh sách và trạng thái tất cả người dùng"}},
    {
        "type": "function", 
        "function": {
            "name": "update_user_status",
            "description": "Khóa hoặc mở khóa người dùng",
            "parameters": {
                "type": "object",
                "properties": {"user_id": {"type": "integer"}, "is_active": {"type": "boolean"}},
                "required": ["user_id", "is_active"]
            }
        }
    },
    
    # ĐƠN HÀNG

    {
        "type": "function",
        "function": {
            "name": "get_recent_orders",
            "description": "Xem danh sách đơn hàng lọc theo trạng thái",
            "parameters": {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "enum": ["Chờ xử lý", "Đang giao", "Đã hoàn thành", "Đã hủy"],
                        "description": "Trạng thái cần lọc"
                    }
                }
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "update_order_status",
            "description": "Cập nhật trạng thái đơn hàng",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "integer",
                        "description": "ID của đơn hàng cần cập nhật"
                    },
                    "new_status": {
                        "type": "string",
                        "enum": ["Chờ xử lý", "Đang giao", "Đã hoàn thành", "Đã hủy"],
                        "description": "Trạng thái mới"
                    }
                },
                "required": ["order_id", "new_status"]
            }
        }
    },

    # ĐÁNH GIÁ
    {
        "type": "function",
        "function": {
            "name": "get_product_reviews",
            "description": "Xem danh sách đánh giá của khách hàng, có thể lọc theo số sao",
            "parameters": {
                "type": "object",
                "properties": {
                    "rating": {"type": "integer", "description": "Số sao cần lọc (1-5)"}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "reply_to_review",
            "description": "Gửi phản hồi của admin cho khách hàng về đánh giá của họ",
            "parameters": {
                "type": "object",
                "properties": {
                    "review_id": {"type": "integer", "description": "ID của đánh giá"},
                    "reply_text": {"type": "string", "description": "Nội dung phản hồi"}
                },
                "required": ["review_id", "reply_text"]
            }
        }
    }
]

def run_admin_agent(user_input):
    try:
        # gửi yêu cầu tới AI
        response = client.chat.completions.create(
            model="gemini-2.5-flash",
            messages=[
                {"role": "system", "content": "Bạn là Quản trị viên cấp cao. Thực thi lệnh chính xác theo yêu cầu."},
                {"role": "user", "content": user_input}
            ],
            tools=AGENT_TOOLS_SCHEMA,
            tool_choice="auto"
        )
        
        msg = response.choices[0].message
    # AI sẽ tự động chọn tool_calls (-> tạo từng đối tượng tool_call chứa name và arguments) or content
        if msg.tool_calls:
            results = []
            for tool_call in msg.tool_calls:
                func_name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)
                func = getattr(tools, func_name)
                # Thực thi func với hàm có tên tương ứng trong tools
                results.append(func(**args))
            return "\n".join(results)
            
        return msg.content
    except Exception as e:
        return f"Lỗi thực thi: {str(e)}"