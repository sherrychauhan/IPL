import requests
import json
import csv
import re
from pathlib import Path
from datetime import datetime, timedelta, timezone

BASE_DIR = Path(__file__).resolve().parent
IST_OFFSET = timedelta(hours=5, minutes=30)

def run_script():
    # Load cache
    cache_file = BASE_DIR / "player_stats_cache.json"
    if cache_file.exists():
        with open(cache_file, "r", encoding="utf-8") as f:
            cache = json.load(f)
    else:
        cache = {}

    # Replace with the desired URL
    url = "https://ipl-stats-sports-mechanic.s3.ap-south-1.amazonaws.com/ipl/feeds/stats/284-toprunsscorers.js?callback=ontoprunsscorers"
    text_content = ""
    text_content2 = ""

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad HTTP responses (4xx, 5xx)
        text_content = response.text  # Extract text content
        text_content = text_content[17:-2]
        #print(text_content)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the URL: {e}")


    # Replace with the desired URL
    url2 = "https://ipl-stats-sports-mechanic.s3.ap-south-1.amazonaws.com/ipl/feeds/stats/284-mostwickets.js?callback=onmostwickets"

    try:
        response2 = requests.get(url2)
        response2.raise_for_status()  # Raise an error for bad HTTP responses (4xx, 5xx)
        text_content2 = response2.text  # Extract text content
        text_content2 = text_content2[14:-2]
        print("success")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the URL: {e}")

    json_data_scorer = json.loads(text_content)
    json_data_bowler = json.loads(text_content2)

    def extract_callback_json(js_text: str, callback_name: str):
        match = re.search(rf"{callback_name}\s*\(", js_text, flags=re.IGNORECASE)
        if not match:
            return None

        start = match.end()
        while start < len(js_text) and js_text[start].isspace():
            start += 1

        if start >= len(js_text) or js_text[start] != "{":
            return None

        depth = 0
        in_string = False
        escape = False
        end = start
        for idx, char in enumerate(js_text[start:], start):
            if escape:
                escape = False
                continue
            if char == "\\":
                escape = True
                continue
            if char == '"':
                in_string = not in_string
            if in_string:
                continue
            if char == '{':
                depth += 1
            elif char == '}':
                depth -= 1
                if depth == 0:
                    end = idx + 1
                    break

        if depth != 0:
            return None

        try:
            return json.loads(js_text[start:end])
        except json.JSONDecodeError:
            return None

    def is_cache_valid(fetch_timestamp_str):
        from datetime import time
        fetch_utc = datetime.fromisoformat(fetch_timestamp_str)
        fetch_ist = fetch_utc + IST_OFFSET
        current_ist = datetime.now(timezone.utc) + IST_OFFSET
        return (fetch_ist.date() == current_ist.date() and 
                current_ist.time() < time(23, 0))

    def fetch_player_2026_batting(client_id: str):
        if client_id in cache and is_cache_valid(cache[client_id]['timestamp']):
            return cache[client_id]['data']
        
        player_url = (
            f"https://ipl-stats-sports-mechanic.s3.ap-south-1.amazonaws.com/ipl/feeds/stats/player/{client_id}-playerstats.js"
        )
        result = None
        try:
            response = requests.get(player_url, timeout=30)
            response.raise_for_status()
            payload = extract_callback_json(response.text, "onPlayerStats")
            if not payload:
                result = None
            else:
                batting_list = payload.get("Batting") or payload.get("batting") or []
                if not isinstance(batting_list, list):
                    result = None
                else:
                    for item in batting_list:
                        if str(item.get("Year")) == "2026":
                            result = item
                            break
        except requests.exceptions.RequestException as e:
            print(f"Error fetching player stats for ID {client_id}: {e}")
            result = None
        
        cache[client_id] = {'data': result, 'timestamp': datetime.now(timezone.utc).isoformat()}
        return result

    def create_missing_batting_entry(bowler, batting_2026):
        return {
            "StrikerName": bowler.get("BowlerName", ""),
            "PlayerId": batting_2026.get("PlayerId", bowler.get("ClientPlayerID", "")) if batting_2026 else bowler.get("ClientPlayerID", ""),
            "Matches": (batting_2026.get("Matches") or "0") if batting_2026 else "0",
            "PlayerDOB": "0000-00-00",
            "RightHandedBat": "",
            "Nationality": "",
            "TCompetitionID": (batting_2026.get("CompetitionId") or "") if batting_2026 else "",
            "TStrikerID": "",
            "TTeamID": "",
            "TeamCode": (batting_2026.get("TeamShortName") or "") if batting_2026 else "",
            "TeamName": (batting_2026.get("TeamName") or "") if batting_2026 else "",
            "CompetitionID": (batting_2026.get("CompetitionId") or "") if batting_2026 else "",
            "TeamID": "",
            "StrikerID": "",
            "Innings": (batting_2026.get("Innings") or "0") if batting_2026 else "0",
            "Extras": "0",
            "TotalRuns": (batting_2026.get("Runs") or "0") if batting_2026 else "0",
            "Balls": (batting_2026.get("Balls") or "0") if batting_2026 else "0",
            "Dotballs": "0",
            "StrikeRate": (batting_2026.get("StrikeRate") or "0") if batting_2026 else "0",
            "DBPercent": "0",
            "DBFreq": "0",
            "BdryFreq": "0",
            "BdryPercent": "0",
            "RPSS": "0",
            "ScoringBalls": "0",
            "Ones": "0",
            "Twos": "0",
            "Threes": "0",
            "Fours": (batting_2026.get("Fours") or "0") if batting_2026 else "0",
            "Sixes": (batting_2026.get("Sixes") or "0") if batting_2026 else "0",
            "Outs": "0",
            "NotOuts": (batting_2026.get("NotOuts") or "0") if batting_2026 else "0",
            "BattingAveragesss": (batting_2026.get("BattingAvg") or "0") if batting_2026 else "0",
            "FiftyPlusRuns": (batting_2026.get("Fifties") or "0") if batting_2026 else "0",
            "Centuries": (batting_2026.get("Hundreds") or "0") if batting_2026 else "0",
            "DoubleCenturies": "0",
            "HighestScore": (batting_2026.get("HighestScore") or "0") if batting_2026 else "0",
            "BattingAverage": (batting_2026.get("BattingAvg") or "0") if batting_2026 else "0",
            "Catches": (batting_2026.get("Catches") or "0") if batting_2026 else "0",
            "Stumpings": (batting_2026.get("Stumpings") or "0") if batting_2026 else "0",
            "ClientPlayerID": bowler.get("ClientPlayerID", ""),
            "Points": 0,
        }

    bowler_names = {player["StrikerName"] for player in json_data_scorer["toprunsscorers"]}
    for bowler in json_data_bowler["mostwickets"]:
        if bowler.get("BowlerName") not in bowler_names:
            batting_2026 = fetch_player_2026_batting(bowler.get("ClientPlayerID", ""))
            json_data_scorer["toprunsscorers"].append(
                create_missing_batting_entry(bowler, batting_2026)
            )
            bowler_names.add(bowler.get("BowlerName"))

    def calculate_points(player):
        q = int(player.get("TotalRuns") or 0)                 # Q Column: Total Runs
        ad = int(player.get("Fours") or 0)                   # AD Column: Fours
        ae = int(player.get("Sixes") or 0)                   # AE Column: Sixes
        ai = int(player.get("FiftyPlusRuns") or 0)           # AI Column: FiftyPlusRuns
        aj = int(player.get("Centuries") or 0)               # AJ Column: Centuries
        an = int(player.get("Catches") or 0)                 # AN Column: Catches
        ao = int(player.get("Stumpings") or 0)               # AO Column: Stumpings

        # Calculate points
        return q + ad + (2 * ae) + (8 * ai) + (aj * 16) + (8 * an) + (ao * 12)

    # Add a new "Points" property for each player
    for player in json_data_scorer["toprunsscorers"]:
        player["Points"] = calculate_points(player)

    def calculate_bowling_points(player):
        af = int(player.get("Wickets", 0))            # Wickets
        am = int(player.get("Maidens", 0))           # Maidens
        ao = int(player.get("FourWickets", 0))       # FourWickets
        ap = int(player.get("FiveWickets", 0))       # FiveWickets
        # Calculate bowling points
        return (25 * af) + (12 * am) + (8 * ao) + (16 * ap)


    # Add the calculated "Points" property to each player
    for player in json_data_bowler["mostwickets"]:
        player["Points"] = calculate_bowling_points(player)

    # Combine data into a third JSON object update the path here
    combined_player_data = []
    existing_client_ids = set()
    conertjsontocsv (json_data_scorer["toprunsscorers"], BASE_DIR / "toprunsscorers.csv") 
    conertjsontocsv (json_data_bowler["mostwickets"], BASE_DIR / "mostwickets.csv") 

    for batting_player in json_data_scorer["toprunsscorers"]:
        # Find matching player in the bowling data
        bowling_player = next(
            (player for player in json_data_bowler["mostwickets"]
            if player["BowlerName"] == batting_player["StrikerName"]),
            None
        )

        # Calculate total points
        if bowling_player:
            total_points = batting_player["Points"] + bowling_player["Points"]
            batting_breakdown = {
                "TotalRuns": batting_player.get("TotalRuns", 0),
                "Fours": batting_player.get("Fours", 0),
                "Sixes": batting_player.get("Sixes", 0),
                "FiftyPlusRuns": batting_player.get("FiftyPlusRuns", 0),
                "Centuries": batting_player.get("Centuries", 0),
                "Catches": batting_player.get("Catches", 0),
                "Stumpings": batting_player.get("Stumpings", 0),
                "BattingPoints": batting_player["Points"]
            }
            bowling_breakdown = {
                "Wickets": bowling_player.get("Wickets", 0),
                "Maidens": bowling_player.get("Maidens", 0),
                "FourWickets": bowling_player.get("FourWickets", 0),
                "FiveWickets": bowling_player.get("FiveWickets", 0),
                "BowlingPoints": bowling_player["Points"]
            }
        else:
            total_points = batting_player["Points"]
            batting_breakdown = {
                "TotalRuns": batting_player.get("TotalRuns", 0),
                "Fours": batting_player.get("Fours", 0),
                "Sixes": batting_player.get("Sixes", 0),
                "FiftyPlusRuns": batting_player.get("FiftyPlusRuns", 0),
                "Centuries": batting_player.get("Centuries", 0),
                "Catches": batting_player.get("Catches", 0),
                "Stumpings": batting_player.get("Stumpings", 0),
                "BattingPoints": batting_player["Points"]
            }
            bowling_breakdown = {
                "Wickets": 0,
                "Maidens": 0,
                "FourWickets": 0,
                "FiveWickets": 0,
                "BowlingPoints": 0
            }

        if batting_player["StrikerName"] not in existing_client_ids:
            # Create combined player data
            combined_player_data.append({
                "PlayerName": batting_player["StrikerName"],
                "ClientPlayerID": batting_player["ClientPlayerID"],
                "Points": total_points,
                "teamName" : batting_player["TeamName"],
                "breakdown": {
                    "batting": batting_breakdown,
                    "bowling": bowling_breakdown
                }
            })
            existing_client_ids.add(batting_player["StrikerName"])
        
        
    for bowling_player in json_data_bowler["mostwickets"]:
        # Find matching player in the bowling data
        batting_player = next(
            (player for player in json_data_scorer["toprunsscorers"]
            if player["StrikerName"] == bowling_player["BowlerName"]),
            None
        )

        # Calculate total points
        if batting_player:
            total_points = batting_player["Points"] + bowling_player["Points"]
            batting_breakdown = {
                "TotalRuns": batting_player.get("TotalRuns", 0),
                "Fours": batting_player.get("Fours", 0),
                "Sixes": batting_player.get("Sixes", 0),
                "FiftyPlusRuns": batting_player.get("FiftyPlusRuns", 0),
                "Centuries": batting_player.get("Centuries", 0),
                "Catches": batting_player.get("Catches", 0),
                "Stumpings": batting_player.get("Stumpings", 0),
                "BattingPoints": batting_player["Points"]
            }
            bowling_breakdown = {
                "Wickets": bowling_player.get("Wickets", 0),
                "Maidens": bowling_player.get("Maidens", 0),
                "FourWickets": bowling_player.get("FourWickets", 0),
                "FiveWickets": bowling_player.get("FiveWickets", 0),
                "BowlingPoints": bowling_player["Points"]
            }
        else:
            total_points = bowling_player["Points"]
            batting_breakdown = {
                "TotalRuns": 0,
                "Fours": 0,
                "Sixes": 0,
                "FiftyPlusRuns": 0,
                "Centuries": 0,
                "Catches": 0,
                "Stumpings": 0,
                "BattingPoints": 0
            }
            bowling_breakdown = {
                "Wickets": bowling_player.get("Wickets", 0),
                "Maidens": bowling_player.get("Maidens", 0),
                "FourWickets": bowling_player.get("FourWickets", 0),
                "FiveWickets": bowling_player.get("FiveWickets", 0),
                "BowlingPoints": bowling_player["Points"]
            }

        # Create combined player data
        if bowling_player["BowlerName"] not in existing_client_ids:
            # Create combined player data
            combined_player_data.append({
                "PlayerName": bowling_player["BowlerName"],
                "ClientPlayerID": bowling_player["ClientPlayerID"],
                "Points": total_points,
                "teamName" : bowling_player["TeamName"],
                "breakdown": {
                    "batting": batting_breakdown,
                    "bowling": bowling_breakdown
                }
               
            })
            existing_client_ids.add(bowling_player["BowlerName"])
        
    # Create a new JSON object
    final_data = {"players": combined_player_data}

    # Load unmatched names from unmatched_names_new.csv and add only those missing from toprunsscorers
    unmatched_file = BASE_DIR / "unmatched_names_new.csv"
    unmatched_players = {}
    if unmatched_file.exists():
        with open(unmatched_file, "r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = row.get("playerName", "").strip()
                client_id = row.get("ClientPlayerID", "").strip()
                if name and client_id:
                    unmatched_players[name] = client_id

    existing_player_names = {p["PlayerName"] for p in final_data["players"]}
    for player_name, client_id in unmatched_players.items():
        if player_name not in existing_player_names:
            batting_2026 = fetch_player_2026_batting(client_id)
            dummy_bowler = {"BowlerName": player_name, "ClientPlayerID": client_id}
            batting_entry = create_missing_batting_entry(dummy_bowler, batting_2026)
            batting_entry["Points"] = calculate_points(batting_entry)
            final_data["players"].append({
                "PlayerName": player_name,
                "ClientPlayerID": client_id,
                "Points": batting_entry["Points"],
                "teamName": batting_entry.get("TeamName", ""),
                "breakdown": {
                    "batting": {
                        "TotalRuns": int(batting_entry.get("TotalRuns", 0)),
                        "Fours": int(batting_entry.get("Fours", 0)),
                        "Sixes": int(batting_entry.get("Sixes", 0)),
                        "FiftyPlusRuns": int(batting_entry.get("FiftyPlusRuns", 0)),
                        "Centuries": int(batting_entry.get("Centuries", 0)),
                        "Catches": int(batting_entry.get("Catches", 0)),
                        "Stumpings": int(batting_entry.get("Stumpings", 0)),
                        "BattingPoints": batting_entry["Points"]
                    },
                    "bowling": {
                        "Wickets": 0,
                        "Maidens": 0,
                        "FourWickets": 0,
                        "FiveWickets": 0,
                        "BowlingPoints": 0
                    }
                }
            })
            existing_player_names.add(player_name)

    with open(BASE_DIR / "OwnerDataPlayer.json", "r", encoding="utf-8") as file:
        players_data = json.load(file)
    print("player2 loaded")

    player_dictionary = {}
    player_teamName_dictionary = {}
    player_breakdown_dictionary = {}

    for f_player in final_data["players"]:
        # Find matching player in the bowling data
        owner_player = next(
            (player for player in players_data
            if player["playerName"] == f_player["PlayerName"]),
            None
        )
        
        if owner_player:
            total_points = f_player["Points"]
            player_dictionary[owner_player["playerName"]] = total_points * ( 1.5 if owner_player["role"] == "Vice-Captain" else 2 if owner_player["role"] == "Captain" else 1)         
            player_teamName_dictionary[owner_player["playerName"]] = f_player["teamName"]
            player_breakdown_dictionary[owner_player["playerName"]] = f_player["breakdown"]

        
    for player in players_data:
        player["points"] = player_dictionary.get(player["playerName"],0)
        player["breakdown"] = player_breakdown_dictionary.get(player["playerName"], {})
        player["role"] = player["role"] + " ("+  player["team"] + ")"

    # File name
    file_name = BASE_DIR / "players_role.json"

    # Writing JSON data to file
    with open(file_name, "w", encoding="utf-8") as json_file:
        json.dump(players_data, json_file, indent=4)

    # Save cache
    with open(cache_file, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=4)

    return f"Data successfully written to {file_name}"

def conertjsontocsv(data, file_name):
    # File name for CSV
    #file_name = 'products.csv'
    
    # Writing JSON data to CSV
    with open(file_name, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=data[0].keys())  # Use keys as field names
        writer.writeheader()  # Write header row
        writer.writerows(data)  # Write data rows

if __name__ == '__main__':
    run_script()