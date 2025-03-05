import json
# import boto3
import os
import requests
# import datetime

# # DynamoDB setup
# dynamodb = boto3.resource("dynamodb", region_name=os.environ["AWS_REGION"])
# table = dynamodb.Table(os.environ["DYNAMODB_TABLE"])

OLLAMA_URL = os.environ["OLLAMA_URL"]  # External API endpoint

# CORS Headers
HEADERS = {
    "Access-Control-Allow-Origin": "https://kokoro.doctor",
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type"
}

CERT_PATH = "kokoro_ssl.pem"

def lambda_handler(event, context):
    body = json.loads(event.get("body", "{}"))
    user_id = body.get("user_id")
    message = body.get("message")
    language = body.get("language", "en")

    if not user_id or not message:
        return {"statusCode": 400, "headers": HEADERS, "body": json.dumps({"error": "User ID and message are required"})}

    # Call Ollama API
    ollama_response = requests.post(OLLAMA_URL, json={"question": message, "language": language}, verify=CERT_PATH)

    
    if ollama_response.status_code != 200:
        return {"statusCode": 500, "headers": HEADERS, "body": json.dumps({"error": "Ollama API Error"})}

    bot_message = ollama_response.json().get("text", "Sorry, I didn't understand.")
    # timestamp = datetime.datetime.utcnow().isoformat()

    # # Save conversation to DynamoDB
    # table.put_item(
    #     Item={
    #         "userId": user_id,
    #         # "timeStamp": timestamp,
    #         "data": {
    #             "user": user_id,
    #             "usermessage": message,
    #             "bot": "Bot",
    #             "botmessage": bot_message
    #         }
    #     }
    # )

    return {"statusCode": 200, "headers": HEADERS, "body": json.dumps({"text": bot_message})}
