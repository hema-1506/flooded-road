import json
import random
import time
from datetime import datetime
import pytz

import boto3
from awscrt import io, mqtt
from awsiot import mqtt_connection_builder

IOT_ENDPOINT = "a1fuz0gf34quva-ats.iot.us-east-1.amazonaws.com"
CLIENT_ID = "flood-simulator"
PATH_TO_CERT = "device.pem.crt"
PATH_TO_KEY = "private.pem.key"
PATH_TO_ROOT = "AmazonRootCA1.pem"
TOPIC = "flood/road/data"

QUEUE_URL = "https://sqs.us-east-1.amazonaws.com/003174967607/FloodSensorQueue"
sqs = boto3.client("sqs", region_name="us-east-1")

ROAD_IDS = ["R1", "R2", "R3", "R4", "R5"]

def generate_sensor_data(road_id):
    return {
        "road_id": road_id,
        "water_depth": random.randint(5, 40),
        "rainfall": random.randint(0, 20),
        "temperature": random.randint(18, 35),
        "vehicle_speed": random.randint(20, 80),
        "humidity": random.randint(40, 90)
    }

def calculate_status(depth):
    if depth > 30:
        return "FLOOD"
    elif depth > 15:
        return "WARNING"
    else:
        return "SAFE"

event_loop_group = io.EventLoopGroup(1)
host_resolver = io.DefaultHostResolver(event_loop_group)
client_bootstrap = io.ClientBootstrap(event_loop_group, host_resolver)

mqtt_connection = mqtt_connection_builder.mtls_from_path(
    endpoint=IOT_ENDPOINT,
    cert_filepath=PATH_TO_CERT,
    pri_key_filepath=PATH_TO_KEY,
    client_bootstrap=client_bootstrap,
    ca_filepath=PATH_TO_ROOT,
    client_id=CLIENT_ID,
    clean_session=False,
    keep_alive_secs=30
)

print("Connecting to AWS IoT Core...")
mqtt_connection.connect().result()
print("Connected to AWS IoT Core!")

while True:
    for road_id in ROAD_IDS:
        sensor = generate_sensor_data(road_id)
        sensor["status"] = calculate_status(sensor["water_depth"])
        dublin = pytz.timezone("UK/London")
        sensor["timestamp"] = datetime.now(UK/London).strftime("%Y-%m-%d %H:%M:%S")

        payload = json.dumps(sensor)

        mqtt_connection.publish(
            topic=TOPIC,
            payload=payload,
            qos=mqtt.QoS.AT_LEAST_ONCE
        )

        sqs.send_message(
            QueueUrl=QUEUE_URL,
            MessageBody=payload
        )

        print("Sent:", sensor)
        time.sleep(1)

    time.sleep(5)