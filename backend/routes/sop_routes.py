import os
import requests # Added this to talk to the AI microservice
from flask import Blueprint, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from models import db, SOPDocument
from routes.common import role_required, get_current_user



sop_bp = Blueprint("sop_bp", __name__)
UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads", "sops")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@sop_bp.get("/sops")
@role_required("admin", "doctor", "nurse")
def get_sops():
    docs = SOPDocument.query.order_by(SOPDocument.created_at.desc()).all()
    return jsonify([{
        "id": d.id, "title": d.title, "category": d.category, 
        "filename": d.filename, "created_at": d.created_at.isoformat()
    } for d in docs]), 200

@sop_bp.post("/sops/upload")
@role_required("admin")
def upload_sop():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    title = request.form.get('title', 'Untitled Document')
    category = request.form.get('category', 'General')

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and file.filename.endswith('.pdf'):
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)

        new_doc = SOPDocument(
            title=title, filename=filename, file_path=file_path,
            category=category, uploaded_by=get_current_user().id
        )
        db.session.add(new_doc)
        db.session.commit()
        return jsonify({"message": "SOP uploaded successfully"}), 201
    return jsonify({"error": "Only PDF files are allowed"}), 400

@sop_bp.get("/sops/<int:doc_id>/view")
def view_sop(doc_id):
    doc = SOPDocument.query.get_or_404(doc_id)
    return send_from_directory(UPLOAD_FOLDER, doc.filename)


@sop_bp.post("/sops/chat")
@role_required("admin", "doctor", "nurse")
def chat_with_sops():
    data = request.get_json()
    user_message = data.get("message")
    
    if not user_message:
         return jsonify({"error": "Message required"}), 400

    try:
        
        ai_service_url = "http://127.0.0.1:5001/api/ask"
        
        
        response = requests.post(
            ai_service_url, 
            json={"message": user_message}, 
            timeout=30 
        )
        
        if response.status_code == 200:
            ai_data = response.json()
            return jsonify({"answer": ai_data.get("answer")}), 200
        else:
            return jsonify({"error": "AI Service returned an error."}), 500
            
    except requests.exceptions.ConnectionError:
        # This gracefully handles the scenario where you forgot to run ai_server.py!
        return jsonify({
    "error": (
        "The AI Engine is currently offline. Please start the microservice:\n"
        "1. Open a new terminal window\n"
        "2. pip install -r requirements.txt\n"
        "3. cd backend\n"
        "4. python ai_server.py"
    )
}), 503
    except Exception as e:
        return jsonify({"error": f"Failed to communicate with AI Engine: {str(e)}"}), 500