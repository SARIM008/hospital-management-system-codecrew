import os
from app import app, db
from models import SOPDocument

# Define your 4 dummy SOPs here
SOP_DATA = [
    {
        "title": "Admission SOP",
        "filename": "SOP_ADMISSION_PROCESS.pdf",
        "category": "General"
    },
    {
        "title": "Discharge SOP",
        "filename": "SOP_Discharge_Process.pdf",
        "category": "General"
    },
    {
        "title": "Emergency-Response SOP.pdf",
        "filename": "SOP_Emergency_Response.pdf",
        "category": "Emergency"
    },
    {
        "title": "Medication-Administration SOP",
        "filename": "SOP_Medication_Administration.pdf",
        "category": "General"
    }
]

def seed_database():
    with app.app_context():
        # Get the absolute path to your uploads/sops folder
        upload_dir = os.path.join(os.getcwd(), "uploads", "sops")
        
        # 1. Clear any existing SOPs to prevent duplicates if you run this twice
        SOPDocument.query.delete()
        
        # 2. Add the new SOPs
        for sop in SOP_DATA:
            file_path = os.path.join(upload_dir, sop["filename"])
            
            new_doc = SOPDocument(
                title=sop["title"],
                filename=sop["filename"],
                file_path=file_path,
                category=sop["category"],
                uploaded_by=1  # Assuming Admin user ID is 1
            )
            db.session.add(new_doc)
            
        db.session.commit()
        print("✅ Successfully seeded 4 SOPs into the database!")

if __name__ == "__main__":
    seed_database()