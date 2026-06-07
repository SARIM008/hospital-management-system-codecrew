# backend/ai_server.py
from flask import Flask, request, jsonify
from services.rag import ChatPDF # Import your existing RAG class

app = Flask(__name__)

# Initialize the heavy AI model ONCE when this specific server boots
print("Initializing Heavy AI RAG Pipeline...")
hospital_rag = ChatPDF()
hospital_rag.load_vector_store()
print("AI Engine is online and ready!")

@app.post("/api/ask")
def ask_ai():
    data = request.get_json()
    user_message = data.get("message")
    
    if not user_message:
        return jsonify({"error": "Message is required"}), 400
        
    try:
        # Let the heavy model process the question
        answer = hospital_rag.ask(user_message)
        return jsonify({"answer": answer}), 200
    except Exception as e:
        print(f"AI Engine Error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    
    app.run(port=5001, debug=False)