from flask import Flask, request, jsonify, render_template
import script  # Import your Python script
import loadpoints
import json
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
app = Flask(
    __name__,
    template_folder=str(BASE_DIR / "templates"),
    static_folder=str(BASE_DIR / "static"),
)

#@app.route('/run-script', methods=['GET'])
#def run_script():
 #   result = script.run_script()  # Call your Python function
  #  return jsonify({"result": result})  # Return the result as JSON

@app.route('/load-points', methods=['GET'])
def run_script():
    result = loadpoints.run_script()  # Call your Python function
    return jsonify({"result": result})  # Return the result as JSON

@app.route('/')
def hello_world():
    return 'Hello from Flask!'

@app.route('/iplpoints')
def Load_ipl_players():
    return render_template("IPLPlayerpoints.html") 

@app.route('/hello')
def hello_world1():
    return 'Hello from F20021k!'


@app.route("/stats")
def home():
    return render_template("stats.html") 

@app.route("/playerStats")
def playerStats():
    return render_template("IPLPlayerStats.html") 


@app.route("/player_role.json", methods=["GET"])
def get_player_data():
    # Read data from the file
    try:
        with open(BASE_DIR / "players_role.json", "r", encoding="utf-8") as file:
            data = json.load(file)  # Load JSON data from the file
        return jsonify(data)  # Return the data as JSON response
    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404  # Return error if file does not exist
    except json.JSONDecodeError:
        return jsonify({"error": "Invalid JSON format"}), 500  # Handle JSON parsing errors


@app.route("/player-role-meta", methods=["GET"])
def get_player_role_meta():
    try:
        file_path = BASE_DIR / "players_role.json"
        if not file_path.exists():
            return jsonify({"error": "File not found"}), 404

        modified_timestamp = file_path.stat().st_mtime
        modified_utc = datetime.fromtimestamp(modified_timestamp, tz=timezone.utc).isoformat()

        return jsonify(
            {
                "file": "players_role.json",
                "last_modified_utc": modified_utc,
                "last_modified_epoch": int(modified_timestamp),
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/players<int:file_no>.json", methods=["GET"])
def get_players_file(file_no):
    try:
        file_path = BASE_DIR / f"players{file_no}.json"
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
        return jsonify(data)
    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404
    except json.JSONDecodeError:
        return jsonify({"error": "Invalid JSON format"}), 500


@app.route("/winnings.json", methods=["GET"])
def get_file_data():
    # Read data from the file
    try:
        with open(BASE_DIR / "winnings.json", "r", encoding="utf-8") as file:
            data = json.load(file)  # Load JSON data from the file
        return jsonify(data)  # Return the data as JSON response
    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404  # Return error if file does not exist
    except json.JSONDecodeError:
        return jsonify({"error": "Invalid JSON format"}), 500  # Handle JSON parsing errors

@app.route("/save-winnings", methods=["POST"])
def save_winnings():
    try:
        # Get the updated data sent from the client
        updated_data = request.json

        # Write the updated data back to the JSON file
        with open(BASE_DIR / "winnings.json", "w", encoding="utf-8") as file:
            json.dump(updated_data, file, indent=4)

        # Return a success response
        return jsonify({"message": "Data saved successfully!"}), 200
    except Exception as e:
        # Handle any errors and return a failure response
        return jsonify({"error": str(e)}), 500

@app.route("/today-fixtures", methods=["GET"])
def get_todays_fixtures():
    try:
        # Load schedule data from schedule.json
        with open(BASE_DIR / "schedule.json", "r", encoding="utf-8") as file:
            schedule_data = json.load(file)

        # Get today's date in the format used in schedule.json
        today_date = datetime.now().strftime("%B %#d, %A")  # Example: "March 22, Saturday"
        print(today_date.strip())
        # Find fixtures matching today's date
        todays_fixtures = [
            {"Match": entry["Match"], "Fixture": entry["Fixture"]}
            for entry in schedule_data if entry["Date"] == today_date
        ]

        # Return the matched fixtures or a no-fixtures message
        if todays_fixtures:
            return jsonify({"date": today_date, "fixtures": todays_fixtures}), 200
        else:
            return jsonify({"date": today_date, "fixtures": []}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
