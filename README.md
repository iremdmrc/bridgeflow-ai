# BridgeFlow AI

BridgeFlow AI is an agentic healthcare workflow assistant that automates
patient registration in legacy healthcare systems using AI.

The system allows users to describe a patient registration request in
natural language. BridgeFlow AI then extracts patient information,
validates the data, detects duplicates, and safely automates the
registration process.

This project was built for the Amazon Nova AI Hackathon.

------------------------------------------------------------------------

## Problem

Many healthcare organizations still rely on legacy portals that require
manual patient registration.
These systems create several problems: - Slow manual workflows - Human
data entry errors - Duplicate patient records - Poor data validation -
Inefficient administrative processes
Healthcare providers need automation that improves efficiency while
maintaining safety and accuracy.

------------------------------------------------------------------------

## Solution

BridgeFlow AI introduces an AI-powered workflow layer between users and
legacy healthcare systems.
Instead of manually filling out forms, users can simply type a request
like:
Register patient John Doe born 1999-05-10 insured Aetna phone 1234567890

BridgeFlow AI automatically: 1. Understands the request using AI 2.
Extracts structured patient information 3. Validates healthcare data 4.
Calculates a confidence score 5. Detects duplicate patients 6. Automates
legacy system registration
If the system detects a potential risk (such as incorrect data or
missing information), it switches to a human-in-the-loop workflow to
ensure safe submission.

------------------------------------------------------------------------

## Key Features

-   Natural language patient registration
-   AI-powered request parsing
-   Risk scoring and validation layer
-   Duplicate patient detection
-   Legacy system automation
-   Patient registry database
-   Human-in-the-loop correction workflow

------------------------------------------------------------------------

## Architecture

User Request 
↓ 
AI Parser (Amazon Nova) 
↓ 
Data Validation Layer 
↓ 
Risk &Confidence Scoring 
↓ 
Duplicate Detection 
↓ 
Automation Agent 
↓ 
Legacy Healthcare Portal 
↓ 
Patient Registry Database

------------------------------------------------------------------------

# Example Scenarios

## Normal Registration

Register patient Emily Carter born 1988-11-22 insured Blue Cross phone
7135551234
Result: - AI extracts patient data - Validation passes - Agent submits
registration - Patient is stored in the database

## Duplicate Patient Detection

Register patient John Doe born 1999-05-10 insured Aetna phone 1234567890
Result: - Existing patient record detected - System prevents duplicate
registration - Warning message displayed

## Risk Detection

Register patient David Kim born 1992-08-30 insured UnitedHealth phone
12345
Result: - Phone number fails validation - Risk level flagged - Legacy
form opens for manual verification

------------------------------------------------------------------------

## Tech Stack

-   Python
-   Flask
-   SQLite
-   Amazon Nova AI
-   Automation agent workflow

------------------------------------------------------------------------

## Project Structure

bridgeflow-ai
│
├─ agent
│  ├─ agent_api.py
│  ├─ agent.py
│  ├─ ai_parser.py
│  ├─ db.py
│  ├─ init_db.py
│  ├─ legacy_agent.py
│  ├─ requirements.txt
│  └─ test_bedrock.py
│
├─ dashboard
│  ├─ public
│  ├─ src
│  ├─ package.json
│  └─ package-lock.json
│
├─ docs
├─ legacy-portal
├─ .gitignore
└─ README.md

------------------------------------------------------------------------

## Running the Project

- Backend
cd agent
pip install -r requirements.txt
python agent_api.py

The backend server runs at: http://127.0.0.1:5000

- Frontend
cd dashboard
npm install
npm start

------------------------------------------------------------------------

## Future Improvements

-   Voice-based patient intake
-   Insurance verification automation
-   Appointment scheduling workflows
-   Integration with real healthcare APIs

------------------------------------------------------------------------

## Hackathon: 
This project was built for the Amazon Nova AI Hackathon.
BridgeFlow AI demonstrates how AI agents can safely automate real-world
healthcare workflows while maintaining human oversight.
