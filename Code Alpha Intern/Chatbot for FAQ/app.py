from flask import Flask, render_template, request, jsonify
from chatbot import FAQChatbot

app = Flask(__name__)
chatbot = FAQChatbot()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "")
    if not user_message.strip():
        return jsonify({"answer": "Please enter a question.", "confidence": 0.0})
    response = chatbot.get_response(user_message)
    return jsonify(response)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
