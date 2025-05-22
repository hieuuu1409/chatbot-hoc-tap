
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
    q = q.lower()
    q = q.replace("mạch khởi động từ đơn", "mạch đơn")
    q = q.replace("mạch khởi động đơn", "mạch đơn")
    q = q.replace("mạch điện mở máy động cơ xoay chiều ba pha bằng khởi động từ đơn", "mạch đơn")
    q = q.replace("mạch khởi động từ kép", "mạch kép")
    q = q.replace("mạch khởi động kép", "mạch kép")
    q = q.replace("mạch điện đảo chiều quay động cơ xoay chiều ba pha bằng khởi đồng từ kép", "mạch kép")
    q = q.replace("mạch điện đảo chiều quay động cơ xoay chiều 3 pha bằng khởi đồng từ kép", "mạch kép")
    q = q.replace("mạch điều khiển tuần tự hai máy bơm", "mạch hai động cơ")
    q = q.replace("mạch điều khiển trình tự hai động cơ", "mạch hai động cơ")
    q = q.replace("mạch 2 động cơ", "mạch hai động cơ")
    q = q.replace("mạch điều khiển trình tự 2 động cơ", "mạch hai động cơ")
    q = q.replace("mạch điều khiển tuần tự 2 máy bơm", "mạch hai động cơ")
    q = q.replace("mạch điều khiển tuần tự hai máy bơm ba pha dùng rơ le thời gian", "mạch hai động cơ")
    q = q.replace("mạch điều khiển tuần tự 2 máy bơm ba pha dùng rơ le thời gian", "mạch hai động cơ")
    q = q.replace("mạch điều khiển tuần tự hai máy bơm 3 pha dùng rơ le thời gian", "mạch hai động cơ")
    q = q.replace("mạch điều khiển tuần tự 2 máy bơm 3 pha dùng rơ le thời gian", "mạch hai động cơ")
    return q

@app.route("/", methods=["GET", "POST"])
def index():
    answer_parts = []
    answer_image = None

    if request.method == "POST":
        question = normalize_question(request.form["question"].strip())
        mapping_keys = mapping.keys()

        if question in ["mạch đơn", "mạch kép", "mạch hai động cơ"]:
            session["context"] = question
            answer_parts = [
                f"<strong>{question.capitalize()} gồm các phần:</strong><br>",
                "- Sơ đồ nguyên lý<br>",
                "- Thiết bị sử dụng<br>",
                "- Nguyên lý làm việc<br>",
                "- Các bước lắp đặt<br>",
                "- Mục tiêu bài học<br>",
                "- Hư hỏng thường gặp<br>",
                "<em>Bạn muốn xem mục nào?</em>"
            ]
        else:
            context = session.get("context")
            full_query = f"{question} {context}" if context else question

            best_match = difflib.get_close_matches(full_query, mapping_keys, n=1, cutoff=0.6)

            if best_match:
                key = best_match[0]
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
                answer_parts.append("Xin lỗi, tôi chưa có câu trả lời phù hợp.")

    return render_template("index.html", answer_parts=answer_parts, answer_image=answer_image)

def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000")

if __name__ == "__main__":
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        threading.Timer(1.0, open_browser).start()

    app.run(debug=True)
