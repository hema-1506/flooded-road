# Flood Monitoring System

This project simulates a smart flood monitoring system using IoT sensors, fog computing, and cloud services.

## Architecture

Sensors → Fog Processing → AWS IoT Core → AWS DynamoDB → Flask Dashboard

## AWS IoT Setup

1. Create an AWS IoT Thing and attach a certificate.
2. Create or attach an IoT Policy with publish permissions to the topic `flood/sensors`.
3. Set the following environment variables before running `fog_processor.py`:
   - `AWS_IOT_ENABLED=true`
   - `AWS_IOT_ENDPOINT=a1fuz0gf34quva-ats.iot.us-east-1.amazonaws.com`
   - `AWS_IOT_TOPIC=flood/sensors`
   - `AWS_IOT_CLIENT_ID=flood-sensor-client`
   - `AWS_IOT_ROOT_CA=C:\path\to\AmazonRootCA1.pem`
   - `AWS_IOT_CERT=C:\path\to\certificate.pem.crt`
   - `AWS_IOT_KEY=C:\path\to\private.pem.key`

   Example:
   ```powershell
   set AWS_IOT_ENABLED=true
   set AWS_IOT_ENDPOINT=a1fuz0gf34quva-ats.iot.us-east-1.amazonaws.com
   set AWS_IOT_TOPIC=flood/sensors
   set AWS_IOT_CLIENT_ID=flood-sensor-client
   set AWS_IOT_ROOT_CA=C:\aws-iot\AmazonRootCA1.pem
   set AWS_IOT_CERT=C:\aws-iot\certificate.pem.crt
   set AWS_IOT_KEY=C:\aws-iot\private.pem.key
   ```

4. Install the MQTT dependency: `pip install paho-mqtt`

You can route AWS IoT messages to DynamoDB with an IoT Rule that writes to your `Flood-Data` table.

## Features

- Real-time sensor simulation
- Road selection (R1–R5)
- Flood status monitoring
- Dynamic dashboard UI
- AWS DynamoDB integration

## Technologies Used

- Python
- Flask
- AWS DynamoDB
- HTML / CSS
- Git & GitHub

## Project Structure

flooded-road  
│  
├── app.py  
├── sensors  
├── fog  
├── backend  
├── templates  
├── static  
└── README.md  

## Dashboard

Displays sensor data including:

- Water Depth
- Rainfall
- Temperature
- Vehicle Speed
- Humidity

## Future Improvements

- Real-time AWS sensor data
- Flood alert notifications
- Map-based road visualization
