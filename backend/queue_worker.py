import boto3
import json
import time

sqs = boto3.client("sqs", region_name="us-east-1")
dynamodb = boto3.resource("dynamodb", region_name="us-east-1")

QUEUE_URL = "https://sqs.us-east-1.amazonaws.com/003174967607/FloodSensorQueue"

table = dynamodb.Table("Flood-Data")

print("Queue worker running...")

while True:

    response = sqs.receive_message(
        QueueUrl=QUEUE_URL,
        MaxNumberOfMessages=5,
        WaitTimeSeconds=10
    )

    messages = response.get("Messages", [])

    for msg in messages:

        data = json.loads(msg["Body"])

        table.put_item(Item=data)

        print("Saved:", data)

        sqs.delete_message(
            QueueUrl=QUEUE_URL,
            ReceiptHandle=msg["ReceiptHandle"]
        )

    time.sleep(2)