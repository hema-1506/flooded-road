from flask import Flask, render_template, request
import boto3
from datetime import datetime, timedelta

app = Flask(__name__)

# DynamoDB connection
dynamodb = boto3.resource("dynamodb", region_name="us-east-1")

# Use history table for graphs + latest values
table = dynamodb.Table("Flood-Data-History")

ROAD_OPTIONS = ["R1", "R2", "R3", "R4", "R5"]


def build_timeseries(road_items, limit=20):
    sorted_items = sorted(
        road_items,
        key=lambda x: x.get("timestamp", ""),
        reverse=False
    )
    recent_records = sorted_items[-limit:]

    timeseries = {
        "timestamps": [],
        "water_depth": [],
        "rainfall": [],
        "temperature": [],
        "vehicle_speed": [],
        "humidity": [],
    }

    for item in recent_records:
        raw_ts = str(item.get("timestamp", ""))
        short_ts = raw_ts[11:19] if len(raw_ts) >= 19 else raw_ts

        timeseries["timestamps"].append(short_ts)
        timeseries["water_depth"].append(float(item.get("water_depth", 0)))
        timeseries["rainfall"].append(float(item.get("rainfall", 0)))
        timeseries["temperature"].append(float(item.get("temperature", 0)))
        timeseries["vehicle_speed"].append(float(item.get("vehicle_speed", 0)))
        timeseries["humidity"].append(float(item.get("humidity", 0)))

    return timeseries


def build_sample_timeseries(limit=20):
    now = datetime.utcnow()
    timestamps = [
        (now - timedelta(minutes=(limit - i) * 5)).strftime("%H:%M:%S")
        for i in range(limit)
    ]

    return {
        "timestamps": timestamps,
        "water_depth": [12 + i * 0.8 for i in range(limit)],
        "rainfall": [2 + (i % 5) * 0.4 for i in range(limit)],
        "temperature": [22 + (i % 4) * 0.7 for i in range(limit)],
        "vehicle_speed": [45 + (i % 8) * 2 for i in range(limit)],
        "humidity": [55 + (i % 6) * 1.5 for i in range(limit)],
    }


def build_sample_sensors():
    now = datetime.utcnow().isoformat(timespec="seconds")
    return {
        "water_depth": 18,
        "rainfall": 3,
        "temperature": 23,
        "vehicle_speed": 52,
        "humidity": 62,
        "status": "DEMO",
        "timestamp": now
    }


@app.route("/")
def dashboard():
    road = request.args.get("road", "R1")

    sensors = {
        "water_depth": 0,
        "rainfall": 0,
        "temperature": 0,
        "vehicle_speed": 0,
        "humidity": 0,
        "status": "NO DATA",
        "timestamp": "No Data"
    }

    timeseries = {
        "timestamps": [],
        "water_depth": [],
        "rainfall": [],
        "temperature": [],
        "vehicle_speed": [],
        "humidity": [],
    }

    use_sample = False

    try:
        response = table.scan()
        items = response.get("Items", [])

        road_items = [item for item in items if item.get("road_id") == road]

        if road_items:
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

            timeseries = build_timeseries(road_items)
        else:
            sensors = build_sample_sensors()
            timeseries = build_sample_timeseries()
            use_sample = True

    except Exception as e:
        print("DynamoDB ERROR:", str(e))
        sensors = build_sample_sensors()
        timeseries = build_sample_timeseries()
        use_sample = True

    # Debug
    print("----- DEBUG -----")
    print("ROAD:", road)
    print("TOTAL ITEMS:", len(items) if 'items' in locals() else 0)
    print("ROAD ITEMS:", len(road_items) if 'road_items' in locals() else 0)
    print("TIMESTAMPS:", timeseries["timestamps"])
    print("WATER:", timeseries["water_depth"])
    print("-----------------")

    return render_template(
        "dashboard.html",
        sensors=sensors,
        road=road,
        timeseries=timeseries,
        use_sample=use_sample,
        road_options=ROAD_OPTIONS
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)