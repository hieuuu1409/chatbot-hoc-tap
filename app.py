from flask import Flask, render_template, request, session
import json
import difflib
import os
import webbrowser
import threading

app = Flask(__name__)
app.secret_key = "123456"

# Load mapping
with open("mapping.json", "r", encoding="utf-8") as f:
    mapping = json.load(f)

# ✅ Hàm chuẩn hóa từ đồng nghĩa
def normalize_question(q):
    q = q.lower().strip()

    # Chuẩn hóa tên các mạch
    q = q.replace("mạch khởi động từ đơn", "mạch đơn")
    q = q.replace("mạch khởi động đơn", "mạch đơn")
    q = q.replace("mạch điện mở máy động cơ xoay chiều ba pha bằng khởi động từ đơn", "mạch đơn")

    q = q.replace("mạch khởi động từ kép", "mạch kép")
    q = q.replace("mạch khởi động kép", "mạch kép")
    q = q.replace("mạch điện đảo chiều quay động cơ xoay chiều ba pha bằng khởi động từ kép", "mạch kép")

    q = q.replace("mạch điều khiển tuần tự hai máy bơm", "mạch hai máy bơm")
    q = q.replace("mạch trình tự hai máy bơm", "mạch hai máy bơm")
    q = q.replace("mạch trình tự 2 máy bơm", "mạch hai máy bơm")
    q = q.replace("mạch 2 máy bơm", "mạch hai máy bơm")

    q = q.replace("mạch điều khiển tuần tự hai động cơ", "mạch hai động cơ")
    q = q.replace("mạch trình tự 2 động cơ", "mạch hai động cơ")
    q = q.replace("mạch 2 động cơ", "mạch hai động cơ")

    # Các từ khóa chức năng
    if "thiết bị sử dụng" not in q:
        q = q.replace("thiết bị", "thiết bị sử dụng")
    if "nguyên lý" in q and "sơ đồ" not in q:
        if "nguyên lý làm việc" not in q:
            q = q.replace("nguyên lý", "nguyên lý làm việc")
    if "các bước lắp đặt" not in q:
        q = q.replace("các bước", "các bước lắp đặt")
    if "mục tiêu bài học" not in q:
        q = q.replace("mục tiêu", "mục tiêu bài học")
    if "hư hỏng thường gặp" not in q:
        q = q.replace("hư hỏng", "hư hỏng thường gặp")
    return q

@app.route("/", methods=["GET", "POST"])
def index():
    answer_parts = []
    answer_image = None

    if request.method == "POST":
        question = normalize_question(request.form["question"].strip())
        mapping_keys = mapping.keys()

        print("🟡 Câu hỏi sau khi chuẩn hóa:", question)

        if question in ["mạch đơn", "mạch kép", "mạch hai động cơ", "mạch hai máy bơm"]:
            session["context"] = question
            print("🟢 Cập nhật context:", question)
            answer_parts = [
                f"<strong>{question.capitalize()} gồm các phần:</strong><br>",
                "- Mục tiêu bài học<br>",
                "- Sơ đồ nguyên lý<br>",
                "- Nguyên lý làm việc<br>",
                "- Thiết bị sử dụng<br>",
                "- Các bước lắp đặt<br>",
                "- Hư hỏng thường gặp<br>",
                "<em>Bạn muốn xem mục nào?</em>"
            ]
        else:
            context = session.get("context")
            if any(k in question for k in ["mạch đơn", "mạch kép", "mạch hai máy bơm"]):
                full_query = question
            else:
                full_query = f"{question} {context}" if context else question

            print("🔎 full_query:", full_query)

            # Ưu tiên khớp chính xác trước
            key = None
            if full_query in mapping:
                key = full_query
                print("✅ Khớp chính xác:", key)
            else:
                matches = difflib.get_close_matches(full_query, mapping_keys, n=1, cutoff=0.6)
                if matches:
                    key = matches[0]
                    print("🌀 Khớp gần đúng:", key)

            if key:
                result = mapping.get(key)

                while isinstance(result, str):
                    result = mapping.get(result)
                    if result is None:
                        break

                if isinstance(result, dict):
                    text = result.get("text", "").replace("\n", "<br>")
                    answer_parts.append(text)
                    answer_image = result.get("image", None)
                else:
                    answer_parts.append(str(result))
            else:
                answer_parts.append("❌ Xin lỗi, tôi chưa có câu trả lời phù hợp.")

    return render_template("index.html", answer_parts=answer_parts, answer_image=answer_image)

def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000")

if __name__ == "__main__":
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        threading.Timer(1.0, open_browser).start()

    app.run(debug=True)
