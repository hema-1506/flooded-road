import os
import boto3
import json
import random
import time
from datetime import datetime

try:
    import paho.mqtt.client as mqtt
except ImportError:
    mqtt = None

# AWS SQS client
sqs = boto3.client("sqs", region_name="us-east-1")

# SQS Queue URL
QUEUE_URL = "https://sqs.us-east-1.amazonaws.com/003174967607/FloodSensorQueue"

# AWS IoT MQTT configuration
AWS_IOT_ENABLED = os.getenv("AWS_IOT_ENABLED", "true").lower() in ("1", "true", "yes")

# Endpoint should be placed here
AWS_IOT_ENDPOINT = os.getenv("AWS_IOT_ENDPOINT", "a1fuz0gf34quva-ats.iot.us-east-1.amazonaws.com")

AWS_IOT_PORT = int(os.getenv("AWS_IOT_PORT", "8883"))
AWS_IOT_TOPIC = os.getenv("AWS_IOT_TOPIC", "flood/sensors")
AWS_IOT_CLIENT_ID = os.getenv("AWS_IOT_CLIENT_ID", "flood-sensor-client")

# Certificate files in your EC2 project folder
AWS_IOT_ROOT_CA = os.getenv("AWS_IOT_ROOT_CA", "AmazonRootCA1.pem")
AWS_IOT_CERT = os.getenv("AWS_IOT_CERT", "device.pem.crt")
AWS_IOT_KEY = os.getenv("AWS_IOT_KEY", "private.pem.key")


# -------- SENSOR GENERATION --------
def generate_sensor_data():
    data = {
        "road_id": "R1",   # fixed road for proper graph flow
        "water_depth": random.randint(5, 40),
        "rainfall": random.randint(0, 20),
        "temperature": random.randint(18, 35),
        "vehicle_speed": random.randint(20, 80),
        "humidity": random.randint(40, 90)
    }
    return data


# -------- MQTT INITIALIZATION --------
def init_mqtt_client():
    if not AWS_IOT_ENABLED:
        print("AWS IoT publishing is disabled (AWS_IOT_ENABLED=false).")
        return None

    if mqtt is None:
        print("paho-mqtt is not installed. Install it with: pip install paho-mqtt")
        return None

    client = mqtt.Client(client_id=AWS_IOT_CLIENT_ID)
    client.tls_set(
        ca_certs=AWS_IOT_ROOT_CA,
        certfile=AWS_IOT_CERT,
        keyfile=AWS_IOT_KEY
    )
    client.tls_insecure_set(False)

    def on_connect(client, userdata, flags, rc):
        status = "connected" if rc == 0 else f"failed ({rc})"
        print(f"AWS IoT MQTT {status}")

    client.on_connect = on_connect

    try:
        client.connect(AWS_IOT_ENDPOINT, AWS_IOT_PORT, keepalive=60)
        client.loop_start()
        return client
    except Exception as e:
        print("AWS IoT connection error:", e)
        return None


# -------- FOG PROCESSING --------
def calculate_status(depth):
    if depth > 30:
        return "FLOOD"
    elif depth > 15:
        return "WARNING"
    else:
        return "SAFE"


mqtt_client = init_mqtt_client()

# -------- MAIN LOOP --------
while True:
    # Generate raw sensor data
    sensor = generate_sensor_data()

    # Fog node processing
    sensor["status"] = calculate_status(sensor["water_depth"])

    # Add timestamp AFTER fog processing
    sensor["timestamp"] = datetime.utcnow().isoformat()

    # Convert to JSON
    payload = json.dumps(sensor)

    # Publish to AWS IoT Core
    if mqtt_client is not None:
        try:
            mqtt_client.publish(AWS_IOT_TOPIC, payload, qos=1)
            print("Published to AWS IoT:", AWS_IOT_TOPIC)
        except Exception as e:
            print("AWS IoT publish error:", e)

    # Send processed payload directly to SQS
    # Keep this enabled so your current dashboard pipeline continues working
    try:
        sqs.send_message(
            QueueUrl=QUEUE_URL,
            MessageBody=payload
        )
        print("Sent to queue:", sensor)
    except Exception as e:
        print("SQS send error:", e)

    # Send every 5 seconds
    time.sleep(5)