from flask import Flask, render_template, request
import boto3

app = Flask(__name__)

# DynamoDB connection (uses IAM role automatically)
dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
table = dynamodb.Table("Flood-Data")


@app.route("/")
def dashboard():

    # Get selected road (default R1)
    road = request.args.get("road", "R1")

    # Default values (prevents UI crash)
    sensors = {
        "water_depth": 0,
        "rainfall": 0,
        "temperature": 0,
        "vehicle_speed": 0,
        "humidity": 0,
        "status": "NO DATA",
        "timestamp": "No Data"
    }

    try:
        # Get all data from DynamoDB
        response = table.scan()
        items = response.get("Items", [])

        # Filter by selected road
        road_items = [item for item in items if item.get("road_id") == road]

        if road_items:
            # Sort by timestamp (latest first)
            latest = sorted(
                road_items,
                key=lambda x: x.get("timestamp", ""),
                reverse=True
            )[0]

            sensors = {
                "water_depth": latest.get("water_depth", 0),
                "rainfall": latest.get("rainfall", 0),
                "temperature": latest.get("temperature", 0),
                "vehicle_speed": latest.get("vehicle_speed", 0),
                "humidity": latest.get("humidity", 0),
                "status": latest.get("status", "UNKNOWN"),
                "timestamp": latest.get("timestamp", "No Data")
            }

    except Exception as e:
        # Log error in terminal but don't crash UI
        print("DynamoDB ERROR:", str(e))

    return render_template(
        "dashboard.html",
        sensors=sensors,
        road=road
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)