import google.generativeai as genai
from PIL import Image, ImageGrab
import io
import base64

genai.configure(api_key="AIzaSyCTQPjvhm5lv1ye_YOS0YV5965OrcGkNj8")

# Create the model
generation_config = {
    "temperature": 1,
    "top_p": 0.95,  # Giới hạn số lượng token có thể được chọn
    "top_k": 25,  # Cân nhắc ít token hơn để cải thiện độ nhất quán
    "max_output_tokens": 2048,  # Giới hạn số token phù hợp với nội dung giáo dục
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
)

model_pic = genai.GenerativeModel(
    model_name="gemini-pro-vision",
    generation_config=generation_config,
)

def get_bot_response(user_input):
    if not user_input.strip():  # Kiểm tra xem input có rỗng không
        return "Vui lòng nhập câu hỏi của bạn."

    prompt = f"""
    Bạn là một trợ lý AI chuyên sâu về Cấu trúc Dữ liệu và Giải thuật, ***được hiệu chỉnh bởi team TPK***. Người dùng đã hỏi: "{user_input}". 

    Hãy trả lời câu hỏi một cách chi tiết, dễ hiểu và tập trung vào nội dung liên quan trực tiếp, cung cấp ví dụ minh họa nếu cần.

    Chủ đề bạn có thể xử lý:
    - **Cấu trúc Dữ liệu**:
    - Danh sách Liên kết (Linked List): cấu trúc, cách hoạt động, các loại danh sách liên kết.
    - Hàng Đợi (Queue): các phương thức chính và ứng dụng thực tế.
    - Ngăn Xếp (Stack): hoạt động và ứng dụng.
    - Cây (Tree): cấu trúc cây, các loại cây, phương pháp duyệt cây.
    - Đồ Thị (Graph): các loại đồ thị, thành phần, thuật toán tìm kiếm.
    - **So sánh Thuật toán**: Ưu, nhược điểm và trường hợp sử dụng.
    - **Phân tích Độ phức tạp**: Big-O notation với ví dụ minh họa.

    **Lưu ý quan trọng khi trả lời:**
    1. Trả lời **ngắn gọn, dễ hiểu** nhưng vẫn đầy đủ chi tiết.
    2. **Chỉ tập trung vào nội dung liên quan trực tiếp.** Bỏ qua các chủ đề không liên quan.
    3. **Không nhắc lại câu hỏi** của người dùng trong câu trả lời.
    4. Nếu cần, **tách ý bằng cách sử dụng gạch đầu dòng hoặc đoạn rõ ràng.**

    Mục tiêu: Giúp người dùng hiểu rõ vấn đề hoặc câu hỏi họ đang gặp phải với ví dụ thực tế khi cần.

    """

    try:
        response = model.generate_content(prompt)
        response.resolve()
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"



def evaluate_code(code):
    try:
        prompt = f"""
        Bạn là một trợ lý AI chuyên về Cấu trúc Dữ liệu và Giải thuật. Khi nhận được đoạn code Python từ người dùng, hãy thực hiện các bước sau:

        **Nhận Dữ Liệu từ Người Dùng**:
           - Yêu cầu người dùng gửi đoạn code Python mà họ muốn bạn đánh giá.
           - Nếu cần, hỏi người dùng về mục đích cụ thể của đoạn code hoặc vấn đề mà họ đang gặp phải.

        **Phân Tích Code**:
           - Đọc và hiểu logic của đoạn code.
           - Xác định các cấu trúc dữ liệu được sử dụng (như danh sách, từ điển, ngăn xếp, hàng đợi, cây, đồ thị, v.v.).
           - Nhận diện các thuật toán và phương pháp mà code đang áp dụng (ví dụ: tìm kiếm, sắp xếp, duyệt cây, v.v.).

        **Giải Thích Các Khái Niệm**:
           - Cung cấp định nghĩa ngắn gọn cho từng cấu trúc dữ liệu và thuật toán được sử dụng trong code.
           - Giải thích cách mà những cấu trúc và thuật toán này giúp giải quyết vấn đề cụ thể trong code.

        **Đánh Giá Hiệu Suất**:
           - Phân tích độ phức tạp về thời gian và không gian của thuật toán.

        **Đưa Ra Gợi Ý Cải Tiến**:
           - Đề xuất cách tối ưu hóa code hoặc cải thiện hiệu suất không cần đưa ra code chỉ đề xuất hướng giải quyết.
           - Cung cấp các nguồn tài liệu hoặc hướng dẫn để người dùng có thể tìm hiểu thêm về các khái niệm đã thảo luận.

        **Code cần đánh giá**:
        {code}
        """
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"



def get_bot_response_with_picture(user_input, img):
    if img is None:
        raise ValueError("No image found in the clipboard")

    # Convert image to base64 for API call
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")  # or appropriate format
    img_str = base64.b64encode(buffered.getvalue()).decode()

    prompt = f"Analyze the following image and answer the question: {user_input}\n(Image: {img_str})"  # Combine text and image info in the prompt

    response = model_pic.generate_content(prompt)  # Use the vision model
    response.resolve()
    return response.text
