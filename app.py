from flask import Flask, render_template, request
import boto3
import datetime

app = Flask(__name__)

dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
table = dynamodb.Table("flood-data")

@app.route("/")
def dashboard():

    road = request.args.get("road", "R1")

    response = table.get_item(
        Key={"road_id": road}
    )

    if "Item" in response:
        sensors = response["Item"]
    else:
        sensors = {
            "road_id": road,
            "water_depth": 0,
            "rainfall": 0,
            "temperature": 0,
            "vehicle_speed": 0,
            "humidity": 0,
            "status": "NO DATA"
        }

    sensors["timestamp"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return render_template(
        "dashboard.html",
        sensors=sensors,
        road=road
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)