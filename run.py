from flask import Flask, render_template, request, jsonify
from Call_api import *
from PIL import Image
import io
import base64
import subprocess  # Thêm thư viện subprocess

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        user_input = request.form.get('user_input', '').strip()
        file = request.files.get('file')

        # 1. Xử lý nếu chỉ có text input
        if user_input and not file:
            print(f"Debug: Nhận câu hỏi từ người dùng: {user_input}")
            try:
                response = get_bot_response(user_input)
                return jsonify({'output': response})
            except Exception as e:
                print(f"Error khi xử lý câu hỏi: {str(e)}")
                return jsonify({'output': f"Error: {str(e)}"})

        # 2. Xử lý nếu có file upload
        if file:
            print(f"Debug: Nhận file từ người dùng: {file.filename}")
            if file.filename.lower().endswith('.py'):  # File Python
                try:
                    code = file.read().decode('utf-8')
                    print(f"Debug: Nội dung file Python:\n{code}")
                    response = evaluate_code(code)
                    return jsonify({'output': response})
                except Exception as e:
                    print(f"Error khi xử lý file Python: {str(e)}")
                    return jsonify({'output': f"Error: {str(e)}"})

            elif file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                try:
                    img = Image.open(file.stream)
                    print("Debug: Đã tải ảnh thành công.")
                    response = get_bot_response_with_picture(user_input, img)
                    return jsonify({'output': response})
                except Exception as e:
                    print(f"Error khi xử lý ảnh: {str(e)}")
                    return jsonify({'output': f"Error: {str(e)}"})

            else:
                return jsonify({'output': "Định dạng file không được hỗ trợ. Chỉ hỗ trợ file .py và ảnh."})

        # 3. Nếu không có input hoặc file
        return jsonify({'output': "Vui lòng nhập câu hỏi hoặc tải lên file!"})

    # GET Request
    return render_template("index.html")



if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5678)