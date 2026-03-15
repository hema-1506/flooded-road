from flask import Flask, render_template, request
import boto3
import datetime

app = Flask(__name__)

dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
table = dynamodb.Table("Flood-Data")

@app.route("/")
def dashboard():

    road = request.args.get("road", "R1")

    try:
        response = table.get_item(Key={"road_id": road})
        sensors = response.get("Item", {})
    except Exception as e:
        print("DynamoDB error:", e)
        sensors = {}

    sensors.setdefault("water_depth", 0)
    sensors.setdefault("rainfall", 0)
    sensors.setdefault("temperature", 0)
    sensors.setdefault("vehicle_speed", 0)
    sensors.setdefault("humidity", 0)
    sensors.setdefault("status", "NO DATA")

    sensors["timestamp"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return render_template(
        "dashboard.html",
        sensors=sensors,
        road=road
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)