def build_prompt(contexts, question, info=""):
    list_content = [c['content'] for c in contexts]
    context_str = "\n\n".join(list_content)

    return f"""
    Bạn là nhân viên tư vấn bán hàng. 
    Thông tin hệ thống: {info} 
    Dựa vào danh sách sản phẩm chi tiết sau để trả lời khách:
    ---
    {context_str}
    ---
    Câu hỏi: {question}
    """