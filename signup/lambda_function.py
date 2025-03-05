import json
import boto3
import bcrypt
import os

# DynamoDB setup
dynamodb = boto3.resource("dynamodb", region_name=os.environ["AWS_REGION"])
users_table = dynamodb.Table(os.environ["DYNAMODB_TABLE"])

# CORS Headers
HEADERS = {
    "Access-Control-Allow-Origin": "https://kokoro.doctor",
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type"
}

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode()

def lambda_handler(event, context):
    body = json.loads(event.get("body", "{}"))
    username = body.get("username")
    email = body.get("email")
    password = body.get("password")

    if not username or not email or not password:
        return {"statusCode": 400, "headers": HEADERS, "body": json.dumps({"error": "All fields are required"})}

    response = users_table.get_item(Key={"email": email})
    if "Item" in response:
        return {"statusCode": 400, "headers": HEADERS, "body": json.dumps({"error": "Email already exists"})}

    hashed_password = hash_password(password)
    users_table.put_item(Item={"username": username, "email": email, "password": hashed_password})

    return {
        "statusCode": 200,
        "headers": HEADERS,
        "body": json.dumps({"message": "User registered successfully"})
    }
