import json
import boto3
import os
from boto3.dynamodb.conditions import Key

# DynamoDB setup
dynamodb = boto3.resource("dynamodb", region_name=os.environ["AWS_REGION"])
table = dynamodb.Table(os.environ["DYNAMODB_TABLE"])

# CORS Headers
HEADERS = {
    "Access-Control-Allow-Origin": "https://kokoro.doctor",
    "Access-Control-Allow-Methods": "GET, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type"
}

def lambda_handler(event, context):
    user_id = event.get("pathParameters", {}).get("user_id")

    if not user_id:
        return {"statusCode": 400, "headers": HEADERS, "body": json.dumps({"error": "User ID is required"})}

    response = table.query(
        KeyConditionExpression=Key("userId").eq(user_id),
        ScanIndexForward=False,  # Retrieve latest messages first
        Limit=5  # Get the most recent 5 messages
    )

    messages = [
        {
            "user": item["data"].get("user", ""),
            "usermessage": item["data"].get("usermessage", ""),
            "bot": item["data"].get("bot", ""),
            "botmessage": item["data"].get("botmessage", "")
        } for item in response.get("Items", [])
    ]

    return {
        "statusCode": 200,
        "headers": HEADERS,
        "body": json.dumps({"user_id": user_id, "messages": messages})
    }
