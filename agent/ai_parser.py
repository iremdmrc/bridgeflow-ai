import boto3
import json
from botocore.config import Config

config = Config(
    region_name="us-east-1",
    read_timeout=300,
    connect_timeout=60
)

client = boto3.client("bedrock-runtime", config=config)

MODEL_ID = "us.amazon.nova-lite-v1:0"

def clean_json(text):
    # remove markdown code blocks
    text = text.replace("```json", "")
    text = text.replace("```", "")
    return text.strip()

def parse_request(user_input):

    prompt = f"""
Extract patient information from this request.

Return ONLY valid JSON with these fields:
name
birthDate
insurance
phone

Request:
{user_input}
"""

    response = client.converse(
        modelId=MODEL_ID,
        messages=[
            {
                "role": "user",
                "content": [{"text": prompt}]
            }
        ]
    )

    text = response["output"]["message"]["content"][0]["text"]

    # clean markdown
    text = clean_json(text)

    try:
        data = json.loads(text)
        return data
    except Exception as e:
        print("Model returned invalid JSON:")
        print(text)
        print("Error:", e)
        return None


if __name__ == "__main__":

    request = "Add patient Elif Kaya born 2002-04-15 insured Aetna phone 5551234567"

    parsed = parse_request(request)

    print("Parsed data:")
    print(parsed)