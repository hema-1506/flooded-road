import boto3
import json
import random
import time
from datetime import datetime

# AWS SQS client
sqs = boto3.client("sqs", region_name="us-east-1")

# SQS Queue URL
QUEUE_URL = "https://sqs.us-east-1.amazonaws.com/003174967607/FloodSensorQueue"


# -------- SENSOR GENERATION --------
def generate_sensor_data():

    data = {
        "road_id": random.choice(["R1", "R2", "R3", "R4", "R5"]),
        "water_depth": random.randint(5, 40),
        "rainfall": random.randint(0, 20),
        "temperature": random.randint(18, 35),
        "vehicle_speed": random.randint(20, 80),
        "humidity": random.randint(40, 90)
    }

    return data


# -------- FOG PROCESSING --------
def calculate_status(depth):

    if depth > 30:
        return "FLOOD"

    elif depth > 15:
        return "WARNING"

    else:
        return "SAFE"


# -------- MAIN LOOP --------
while True:

    # Generate raw sensor data
    sensor = generate_sensor_data()

    # Fog node processing
    sensor["status"] = calculate_status(sensor["water_depth"])

    # Add timestamp AFTER fog processing
    sensor["timestamp"] = datetime.utcnow().isoformat()

    # Send processed payload to SQS
    sqs.send_message(
        QueueUrl=QUEUE_URL,
        MessageBody=json.dumps(sensor)
    )

    print("Sent to queue:", sensor)

    # Send every 5 seconds
    time.sleep(5)
