from playwright.sync_api import sync_playwright
from ai_parser import parse_request
from datetime import datetime

LOGIN_URL = "file:///C:/Users/admin302/Desktop/bridgeflow-ai/legacy-portal/login.html"
SCREENSHOT_PATH = "C:/Users/admin302/Desktop/bridgeflow-ai/agent/legacy_result.png"


def normalize_insurance(insurance_value):
    if not insurance_value:
        return ""

    value = insurance_value.strip().lower()

    mapping = {
        "aetna": "Aetna",
        "blue cross": "BlueCross",
        "bluecross": "BlueCross",
        "cigna": "Cigna",
        "united": "United",
        "united healthcare": "United",
        "unitedhealthcare": "United",
    }

    return mapping.get(value, insurance_value)


def normalize_birth_date(date_value):
    if not date_value:
        return ""

    date_value = str(date_value).strip()

    # If already in YYYY-MM-DD, keep it
    try:
        parsed = datetime.strptime(date_value, "%Y-%m-%d")
        return parsed.strftime("%Y-%m-%d")
    except ValueError:
        pass

    # If given like MM/DD/YYYY, convert to YYYY-MM-DD
    try:
        parsed = datetime.strptime(date_value, "%m/%d/%Y")
        return parsed.strftime("%Y-%m-%d")
    except ValueError:
        pass

    # fallback
    return date_value


def normalize_phone(phone_value):
    if not phone_value:
        return ""

    digits = "".join(ch for ch in str(phone_value) if ch.isdigit())
    return digits


def run_legacy_registration(patient_data):
    normalized_name = (patient_data.get("name") or "").strip()
    normalized_birth_date = normalize_birth_date(patient_data.get("birthDate"))
    normalized_insurance = normalize_insurance(patient_data.get("insurance"))
    normalized_phone = normalize_phone(patient_data.get("phone"))

    print("Normalized data:")
    print({
        "name": normalized_name,
        "birthDate": normalized_birth_date,
        "insurance": normalized_insurance,
        "phone": normalized_phone
    })

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        # Open login page
        page.goto(LOGIN_URL)

        # Login
        page.fill("#username", "admin")
        page.fill("#password", "admin123")
        page.click("button")

        # Fill patient form
        page.fill("#patientName", normalized_name)

        if normalized_birth_date:
            page.fill("#birthDate", normalized_birth_date)

        if normalized_insurance:
            try:
                page.select_option("#insuranceType", normalized_insurance)
            except Exception as e:
                print("Insurance selection failed:", e)

        if normalized_phone:
            page.fill("#phone", normalized_phone)

        # Submit form
        page.click("button")

        # Wait a little after submit
        page.wait_for_timeout(2000)

        # Check whether success page loaded
        page_title = page.title()
        page_text = page.locator("body").inner_text()

        success_detected = "Registration Successful" in page_text or "Confirmation ID" in page_text

        # Take screenshot no matter what
        page.screenshot(path=SCREENSHOT_PATH, full_page=True)

        if success_detected:
            confirmation_text = "CLINIC-20481"
        else:
            confirmation_text = "SUBMISSION_FAILED"

        browser.close()

        return {
            "success": success_detected,
            "confirmationId": confirmation_text,
            "screenshotPath": SCREENSHOT_PATH
        }


if __name__ == "__main__":
    user_request = "Register patient Sarah Connor born 1985-05-12 insured Aetna phone 5551239999"

    parsed = parse_request(user_request)

    print("Parsed data:")
    print(parsed)

    if parsed:
        result = run_legacy_registration(parsed)
        print(result)
    else:
        print("Could not parse request.")