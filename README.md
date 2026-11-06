# Hospital Management System - Setup Guide

> **Team project by CodeCrew** for the IIT Madras Software Engineering course (Best Course Project, Rank 1).
> Original repo with full commit history: https://github.com/21f2001224-cmd/team-CodeCrew-se-project
> My role: Scrum Master.
>
> **Team members (contributors in the original repo):** [rishabhcdb](https://github.com/rishabhcdb), [gayathri-srinii](https://github.com/gayathri-srinii)
>
> This repository is a single-commit copy of that project; see the original repo for each member's commits.

## Prerequisites

- Python 3.8+
- Node.js 16+
- npm

If Node.js and npm are not installed, download and install them from https://nodejs.org. npm is included with the Node.js installer.

---

## Installation and Setup

### 1. Install Python Dependencies

From the root of the project folder, run:

```
pip install -r requirements.txt
```

### 2. Start the Backend Server

Open a terminal and run:

```
cd backend
python app.py
```

### 3. Start the Frontend

Open a new terminal and run:

```
cd frontend
npm run dev
```

### 4. Start the AI Server

Open another new terminal and run:

```
cd backend
python ai_server.py
```

### 5. Environment variables configuration

Add a .env file in the root folder and add the following variable along with its API key for using the AI features:
DEEPSEEK_API_KEY=YOUR DEEPSEEK API KEY


### 6. Open the Application

Navigate to the following URL in your browser:

```
http://localhost:5173
```

---

## Note on First-Time Voice Transcription

The application uses the `openai-whisper` library for transcription of doctor consultations. On the first use of the voice recording feature, the transcription model will be downloaded automatically. This is a one-time process and may take a few minutes depending on your internet connection. Subsequent runs will use the cached model.

---

## Note on AI Server Compatibility

The AI/RAG server (`ai_server.py`) powers the SOP search functionality. Some of its dependencies may have version compatibility issues depending on your environment. If you encounter errors while starting the AI server, check the error message and try adjusting the relevant library versions or search for the error online. The core application (appointments, IPD/OPD management, patient records, doctor dashboard) will run fully without the AI server. Only the SOP search feature will be unavailable.

---

## Note on AI/RAG Vector database

The documents ingested in the vector database (in /backend/services/SOP_chromaDB) need to be reingested for every system, if the feature is required to be used.

---

## Project Overview

A full-stack hospital management system serving three user roles: Admin, Doctor, and Patient. It covers outpatient (OPD) and inpatient (IPD) workflows, AI-assisted consultation transcription, and document-grounded SOP search.

---

### User Roles and Features

#### Admin

Admins represent all hospital staff including nurses, ward boys, and the owner.

- Register new patients and book appointments on their behalf (walk-in or over-call)
- Cap the number of appointments per hour to manage peak-hour load and distribute traffic across the day
- Admit patients to IPD and record vitals, progress notes, and medications throughout their stay
- Discharge IPD patients
- Register new doctors and staff members
- View all patients across OPD, IPD, and discharged categories
- Search hospital SOPs using an AI/RAG-powered document search tool (requires AI server)
- Basic inventory management (concept feature)

#### Doctor

- View upcoming appointments assigned to them
- Record consultations via voice; the recording is transcribed using Whisper and sent to an LLM, which returns structured fields: patient complaints, diagnosis, and recommendations. These are stored against the patient's record.
- View and update IPD patient details including vitals and progress notes

#### Patient

- Browse doctors by specialization (e.g. General, ENT, Cardiac) and book an appointment
- View past OPD records: each consultation shows the date, doctor, complaints, diagnosis, and recommendations derived from the voice recording
- View past IPD admissions: each admission shows the diagnosis, latest recorded vitals, and a full list of medications with dosages administered during the stay

---

### Key Flows

**OPD Consultation Flow**

Patient or Admin books appointment -> Doctor records consultation via voice -> Audio is transcribed by Whisper -> Transcript is processed by LLM -> Structured summary (complaints, diagnosis, recommendations) is saved -> Visible to both Doctor and Patient

**IPD Admission Flow**

Admin admits patient -> Staff records vitals, progress notes, and medications over the course of the stay -> Patient and authorized staff can view the full history -> Admin discharges the patient when ready