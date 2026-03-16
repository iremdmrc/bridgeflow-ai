from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from ai_parser import parse_request
from legacy_agent import run_legacy_registration
from db import (
    init_db,
    seed_sample_data,
    find_duplicate_patient,
    save_patient,
    get_recent_patients as fetch_recent_patients
)
import os

app = Flask(__name__)
CORS(app)

SCREENSHOT_FILE = "C:/Users/admin302/Desktop/bridgeflow-ai/agent/legacy_result.png"

init_db()
seed_sample_data()


def calculate_confidence(parsed, missing_fields):
    score = 100

    if missing_fields:
        score -= len(missing_fields) * 20

    if parsed.get("phone"):
        phone = str(parsed.get("phone")).strip()
        if len(phone) < 10:
            score -= 10

    if parsed.get("birthDate"):
        birth = str(parsed.get("birthDate")).strip()
        if len(birth) != 10:
            score -= 10

    if score < 0:
        score = 0

    return score


def calculate_risk_level(parsed, missing_fields):
    critical_missing_count = len(missing_fields)

    if critical_missing_count >= 2:
        return "High Risk"

    if "Birth Date" in missing_fields or "Phone" in missing_fields:
        return "Medium Risk"

    phone = str(parsed.get("phone", "")).strip()
    birth = str(parsed.get("birthDate", "")).strip()

    if phone and len(phone) < 10:
        return "Medium Risk"

    if birth and len(birth) != 10:
        return "Medium Risk"

    return "Low Risk"


def build_suggestions(parsed, missing_fields):
    suggestions = []

    if "Birth Date" in missing_fields:
        suggestions.append("Provide Birth Date in YYYY-MM-DD format.")

    if "Phone" in missing_fields:
        suggestions.append("Provide a valid 10-digit phone number.")

    if "Patient Name" in missing_fields:
        suggestions.append("Include the patient's full name.")

    if "Insurance" in missing_fields:
        suggestions.append("Specify the insurance provider name.")

    if missing_fields:
        name = parsed.get("name") or "[Patient Name]"
        insurance = parsed.get("insurance") or "[Insurance]"
        birth_date = parsed.get("birthDate") or "[YYYY-MM-DD]"
        phone = parsed.get("phone") or "[10-digit phone]"

        suggested_request = (
            f"Register patient {name} born {birth_date} insured {insurance} phone {phone}"
        )
    else:
        suggested_request = None

    return suggestions, suggested_request


@app.route("/legacy-screenshot", methods=["GET"])
def legacy_screenshot():
    if os.path.exists(SCREENSHOT_FILE):
        return send_file(SCREENSHOT_FILE, mimetype="image/png")
    return jsonify({"error": "Screenshot not found"}), 404


@app.route("/recent-patients", methods=["GET"])
def recent_patients_route():
    return jsonify(fetch_recent_patients())


@app.route("/run-agent", methods=["POST"])
def run_agent():
    data = request.get_json(silent=True) or {}
    user_request = data.get("request", "")

    logs = []
    reasoning = []

    reasoning.append("Understanding healthcare intake request")
    reasoning.append("Extracting patient attributes from natural language")
    reasoning.append("Checking required healthcare fields")

    logs.append("[AI] Parsing user request...")

    parsed = parse_request(user_request)

    if not parsed:
        logs.append("[Error] Could not parse request.")
        return jsonify({
            "success": False,
            "logs": logs,
            "parsed": {},
            "confirmationId": None,
            "reasoning": reasoning,
            "confidenceScore": 0,
            "suggestions": [
                "Please provide patient name, birth date, insurance, and phone number."
            ],
            "suggestedRequest": "Register patient [Patient Name] born [YYYY-MM-DD] insured [Insurance] phone [10-digit phone]",
            "screenshotPath": None,
            "riskLevel": "High Risk",
            "duplicatePatient": None,
            "recentPatients": fetch_recent_patients()
        }), 400

    missing_fields = []

    if not parsed.get("name"):
        missing_fields.append("Patient Name")

    if not parsed.get("birthDate"):
        missing_fields.append("Birth Date")

    if not parsed.get("insurance"):
        missing_fields.append("Insurance")

    if not parsed.get("phone"):
        missing_fields.append("Phone")

    confidence_score = calculate_confidence(parsed, missing_fields)
    risk_level = calculate_risk_level(parsed, missing_fields)
    suggestions, suggested_request = build_suggestions(parsed, missing_fields)

    if missing_fields:
        logs.append("[AI] Extracted partial patient information.")
        logs.append("[Validation] Missing required fields:")

        for field in missing_fields:
            logs.append(f"[Validation] {field} is missing")

        reasoning.append("Detected missing required healthcare fields")
        reasoning.append("Preparing smart completion suggestions")

        return jsonify({
            "success": False,
            "logs": logs,
            "parsed": parsed,
            "confirmationId": None,
            "reasoning": reasoning,
            "confidenceScore": confidence_score,
            "suggestions": suggestions,
            "suggestedRequest": suggested_request,
            "screenshotPath": None,
            "riskLevel": risk_level,
            "duplicatePatient": None,
            "recentPatients": fetch_recent_patients()
        }), 400

    reasoning.append("All required fields present")
    reasoning.append("Checking for possible duplicate patient records")

    duplicate_patient = find_duplicate_patient(
        parsed.get("name", ""),
        parsed.get("birthDate", ""),
        parsed.get("phone", "")
    )

    if duplicate_patient:
        logs.append("[Duplicate Check] Potential duplicate patient detected.")
        logs.append(f"[Duplicate Check] Existing patient: {duplicate_patient['name']}")
        logs.append(
            f"[Duplicate Check] Existing confirmation ID: {duplicate_patient['confirmationId']}"
        )

        reasoning.append("Detected a possible duplicate patient record")
        reasoning.append("Stopped legacy submission to prevent duplicate registration")

        return jsonify({
            "success": False,
            "logs": logs,
            "parsed": parsed,
            "confirmationId": None,
            "reasoning": reasoning,
            "confidenceScore": confidence_score,
            "suggestions": [
                "Review the existing patient record before creating a new registration.",
                "Confirm whether this should update an existing patient instead of creating a duplicate."
            ],
            "suggestedRequest": None,
            "screenshotPath": None,
            "riskLevel": "High Risk",
            "duplicatePatient": duplicate_patient,
            "recentPatients": fetch_recent_patients()
        }), 409

    reasoning.append("No duplicate patient detected")
    reasoning.append("Preparing legacy system submission")

    logs.append("[AI] Extracted patient information.")
    logs.append(f"[Data] Name: {parsed['name']}")
    logs.append(f"[Data] Birth Date: {parsed['birthDate']}")
    logs.append(f"[Data] Insurance: {parsed['insurance']}")
    logs.append(f"[Data] Phone: {parsed['phone']}")
    logs.append("[Agent] Opening legacy system...")
    logs.append("[Agent] Logging in...")
    logs.append("[Agent] Filling patient form...")
    logs.append("[Agent] Submitting registration...")

    legacy_result = run_legacy_registration(parsed)

    if legacy_result.get("success"):
        logs.append("[Agent] Patient successfully registered.")
        logs.append(f"[Agent] Confirmation ID: {legacy_result.get('confirmationId')}")
        logs.append("[Agent] Screenshot captured successfully.")

        print(
            "Saving patient to database:",
            parsed["name"],
            parsed["birthDate"],
            parsed["insurance"],
            parsed["phone"],
            legacy_result.get("confirmationId")
        )

        save_patient(
            parsed["name"],
            parsed["birthDate"],
            parsed["insurance"],
            parsed["phone"],
            legacy_result.get("confirmationId")
        )

        return jsonify({
            "success": True,
            "logs": logs,
            "parsed": parsed,
            "confirmationId": legacy_result.get("confirmationId"),
            "reasoning": reasoning,
            "confidenceScore": confidence_score,
            "suggestions": [],
            "suggestedRequest": None,
            "screenshotPath": "http://127.0.0.1:5000/legacy-screenshot",
            "riskLevel": risk_level,
            "duplicatePatient": None,
            "recentPatients": fetch_recent_patients()
        }), 200

    logs.append("[Agent] Submission failed in legacy system.")

    return jsonify({
        "success": False,
        "logs": logs,
        "parsed": parsed,
        "confirmationId": None,
        "reasoning": reasoning,
        "confidenceScore": confidence_score,
        "suggestions": [
            "Legacy system submission failed. Review the mapped form fields and retry."
        ],
        "suggestedRequest": None,
        "screenshotPath": "http://127.0.0.1:5000/legacy-screenshot" if os.path.exists(SCREENSHOT_FILE) else None,
        "riskLevel": "High Risk",
        "duplicatePatient": None,
        "recentPatients": fetch_recent_patients()
    }), 500


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)