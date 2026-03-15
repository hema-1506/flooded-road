import boto3
import json
from decimal import Decimal

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("Flood-Data")

def convert_decimal(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

def lambda_handler(event, context):

    response = table.scan()
    items = response["Items"]

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps(items, default=convert_decimal)
    }
