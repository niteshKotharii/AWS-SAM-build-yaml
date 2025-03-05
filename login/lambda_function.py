import json
import boto3
import bcrypt
import jwt
import os
from datetime import datetime, timedelta, timezone

# Environment variables
SECRET_KEY = os.environ["SECRET_KEY"]
ALGORITHM = os.environ["ALGORITHM"]
TOKEN_EXPIRY_MINUTES = int(os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"])

# DynamoDB setup
dynamodb = boto3.resource("dynamodb", region_name=os.environ["AWS_REGION"])
users_table = dynamodb.Table(os.environ["DYNAMODB_TABLE"])

# CORS Headers
HEADERS = {
    "Access-Control-Allow-Origin": "https://kokoro.doctor",
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type"
}

def verify_password(plain_password, hashed_password):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode())

def create_access_token(email):
    expire = datetime.now(timezone.utc) + timedelta(minutes=TOKEN_EXPIRY_MINUTES)
    return jwt.encode({"sub": email, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)

def lambda_handler(event, context):
    body = json.loads(event.get("body", "{}"))
    email = body.get("email")
    password = body.get("password")

    if not email or not password:
        return {"statusCode": 400, "headers": HEADERS, "body": json.dumps({"error": "Email and password are required"})}

    response = users_table.get_item(Key={"email": email})
    if "Item" not in response:
        return {"statusCode": 400, "headers": HEADERS, "body": json.dumps({"error": "User not found"})}

    stored_user = response["Item"]
    if not verify_password(password, stored_user["password"]):
        return {"statusCode": 400, "headers": HEADERS, "body": json.dumps({"error": "Incorrect password"})}

    token = create_access_token(email)
    return {
        "statusCode": 200,
        "headers": HEADERS,
        "body": json.dumps({
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "name": stored_user.get("username"),
                "email": stored_user.get("email")
            }
        })
    }