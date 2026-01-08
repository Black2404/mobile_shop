def build_prompt(contexts, question):
    # Lấy nội dung text từ danh sách sản phẩm
    list_content = [c['content'] for c in contexts]
    context_str = "\n\n".join(list_content)

    if not context_str:
        return f"""
        Bạn là trợ lý ảo. Khách hàng hỏi: "{question}"
        Hãy trả lời lịch sự rằng bạn không tìm thấy thông tin sản phẩm này trong cửa hàng.
        """

    return f"""
    Bạn là nhân viên tư vấn bán hàng. Dựa vào thông tin sau để trả lời khách:
    ---
    {context_str}
    ---
    Câu hỏi: {question}
    Trả lời ngắn gọn, thân thiện.
    """