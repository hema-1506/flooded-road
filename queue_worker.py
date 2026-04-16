import boto3
import json
import time

REGION = "us-east-1"
QUEUE_URL = "https://sqs.us-east-1.amazonaws.com/003174967607/FloodSensorQueue"

sqs = boto3.client("sqs", region_name=REGION)
dynamodb = boto3.resource("dynamodb", region_name=REGION)
table = dynamodb.Table("Flood-Data-History")

print("Queue worker running...")

while True:
    response = sqs.receive_message(
        QueueUrl=QUEUE_URL,
        MaxNumberOfMessages=1,
        WaitTimeSeconds=10
    )

    messages = response.get("Messages", [])

    if not messages:
        continue

    for message in messages:
        try:
            body = json.loads(message["Body"])

            item = {
                "road_id": body["road_id"],
                "timestamp": body["timestamp"],
                "water_depth": body["water_depth"],
                "rainfall": body["rainfall"],
                "temperature": body["temperature"],
                "vehicle_speed": body["vehicle_speed"],
                "humidity": body["humidity"],
                "status": body["status"]
            }

            table.put_item(Item=item)
            print("Saved to Flood-Data-History:", item)

            sqs.delete_message(
                QueueUrl=QUEUE_URL,
                ReceiptHandle=message["ReceiptHandle"]
            )

        except Exception as e:
            print("Error processing message:", str(e))

    time.sleep(1)