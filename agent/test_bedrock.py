import boto3
from botocore.config import Config

def main():
    config = Config(
        region_name="us-east-1",
        read_timeout=300,
        connect_timeout=60,
        retries={"max_attempts": 2}
    )

    client = boto3.client("bedrock-runtime", config=config)

    model_id = "us.amazon.nova-lite-v1:0"

    response = client.converse(
        modelId=model_id,
        messages=[
            {
                "role": "user",
                "content": [
                    {"text": "Say hello and confirm the connection is working."}
                ]
            }
        ]
    )

    output = response["output"]["message"]["content"][0]["text"]
    print("Model response:")
    print(output)

if __name__ == "__main__":
    main()