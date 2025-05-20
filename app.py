from flask import Flask, render_template, request
import json
import difflib
import os
import webbrowser
import threading

app = Flask(__name__)

# Load mapping
with open("mapping.json", "r", encoding="utf-8") as f:
    mapping = json.load(f)

@app.route("/", methods=["GET", "POST"])
def index():
    answer_text = None
    answer_image = None

    if request.method == "POST":
        question = request.form["question"].strip().lower()
        best_match = difflib.get_close_matches(question, mapping.keys(), n=1, cutoff=0.6)

        if best_match:
            key = best_match[0]
            result = mapping.get(key)

            # 🔁 Nếu là alias (chuỗi), tìm đến kết quả cuối cùng là dict
            while isinstance(result, str):
                result = mapping.get(result)
                if result is None:
                    break

            if isinstance(result, dict):
                answer_text = result.get("text", "")
                answer_image = result.get("image", None)
            else:
                answer_text = result if result else "Xin lỗi, tôi chưa có câu trả lời phù hợp."
                answer_image = None
        else:
            answer_text = "Xin lỗi, tôi chưa có câu trả lời phù hợp."

    return render_template("index.html", answer_text=answer_text, answer_image=answer_image)

def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000")

if __name__ == "__main__":
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        threading.Timer(1.0, open_browser).start()

    app.run(debug=True)
