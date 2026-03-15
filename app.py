from flask import Flask, render_template, request
import datetime

app = Flask(__name__)

# -------- MOCK SENSOR DATA FOR EACH ROAD --------
roads_data = {

    "R1": {
        "water_depth": 19.3,
        "rainfall": 54.28,
        "temperature": 19.53,
        "vehicle_speed": 60.94,
        "humidity": 81.12,
        "status": "SAFE"
    },

    "R2": {
        "water_depth": 35.2,
        "rainfall": 70.10,
        "temperature": 18.2,
        "vehicle_speed": 40.1,
        "humidity": 88.3,
        "status": "WARNING"
    },

    "R3": {
        "water_depth": 60.1,
        "rainfall": 92.4,
        "temperature": 17.9,
        "vehicle_speed": 25.2,
        "humidity": 95.2,
        "status": "FLOOD"
    },

    "R4": {
        "water_depth": 21.5,
        "rainfall": 45.6,
        "temperature": 20.4,
        "vehicle_speed": 55.2,
        "humidity": 70.2,
        "status": "SAFE"
    },

    "R5": {
        "water_depth": 42.8,
        "rainfall": 75.5,
        "temperature": 18.9,
        "vehicle_speed": 35.8,
        "humidity": 90.5,
        "status": "WARNING"
    }
}

@app.route("/")
def dashboard():

    road = request.args.get("road", "R1")

    sensors = roads_data.get(road)

    sensors["timestamp"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return render_template("dashboard.html", sensors=sensors, road=road)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
