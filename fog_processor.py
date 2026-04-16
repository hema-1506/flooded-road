import json
import random
import time
from datetime import datetime

import boto3
from awscrt import io, mqtt
from awsiot import mqtt_connection_builder

# -------- AWS IOT CORE SETTINGS --------
IOT_ENDPOINT = "a1fuz0gf34quva-ats.iot.us-east-1.amazonaws.com"
CLIENT_ID = "flood-simulator"
PATH_TO_CERT = "device.pem.crt"
PATH_TO_KEY = "private.pem.key"
PATH_TO_ROOT = "AmazonRootCA1.pem"
TOPIC = "flood/road/data"

# -------- SQS SETTINGS --------
QUEUE_URL = "https://sqs.us-east-1.amazonaws.com/003174967607/FloodSensorQueue"
sqs = boto3.client("sqs", region_name="us-east-1")


# -------- SENSOR GENERATION --------
def generate_sensor_data():
    data = {
        "road_id": "R1",  # fixed road for graph flow
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


# -------- MQTT CONNECTION --------
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


# -------- MAIN LOOP --------
while True:
    sensor = generate_sensor_data()

    # Fog processing
    sensor["status"] = calculate_status(sensor["water_depth"])
    sensor["timestamp"] = datetime.utcnow().isoformat()

    payload = json.dumps(sensor)

    # Publish to IoT Core
    mqtt_connection.publish(
        topic=TOPIC,
        payload=payload,
        qos=mqtt.QoS.AT_LEAST_ONCE
    )
    print("Published to IoT Core:", sensor)

    # Direct send to SQS
    sqs.send_message(
        QueueUrl=QUEUE_URL,
        MessageBody=payload
    )
    print("Sent to queue:", sensor)

    time.sleep(10)