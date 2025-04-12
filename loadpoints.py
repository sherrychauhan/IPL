import requests
import json

# Replace with the desired URL
url = "https://ipl-stats-sports-mechanic.s3.ap-south-1.amazonaws.com/ipl/feeds/stats/203-toprunsscorers.js?callback=ontoprunsscorers&_=1743434654434"

try:
    response = requests.get(url)
    response.raise_for_status()  # Raise an error for bad HTTP responses (4xx, 5xx)
    text_content = response.text  # Extract text content
    text_content = text_content[17:-2]
    #print(text_content)
except requests.exceptions.RequestException as e:
    print(f"Error fetching the URL: {e}")


# Replace with the desired URL
url2 = "https://ipl-stats-sports-mechanic.s3.ap-south-1.amazonaws.com/ipl/feeds/stats/203-mostwickets.js?callback=onmostwickets&_=1743434870207"

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

def calculate_points(player):
    q = int(player.get("TotalRuns", 0))                 # Q Column: Total Runs
    ad = int(player.get("Fours", 0))                   # AD Column: Fours
    ae = int(player.get("Sixes", 0))                   # AE Column: Sixes
    ai = int(player.get("FiftyPlusRuns", 0))           # AI Column: FiftyPlusRuns
    aj = int(player.get("Centuries", 0))               # AJ Column: Centuries
    an = int(player.get("Catches", 0))                 # AN Column: Catches
    ao = int(player.get("Stumpings", 0))               # AO Column: Stumpings

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

# Combine data into a third JSON object
combined_player_data = []
existing_client_ids = set()
for batting_player in json_data_scorer["toprunsscorers"]:
    # Find matching player in the bowling data
    bowling_player = next(
        (player for player in json_data_bowler["mostwickets"]
         if player["ClientPlayerID"] == batting_player["ClientPlayerID"]),
        None
    )

    # Calculate total points
    if bowling_player:
        total_points = batting_player["Points"] + bowling_player["Points"]
    else:
        total_points = batting_player["Points"]

    if batting_player["ClientPlayerID"] not in existing_client_ids:
        # Create combined player data
        combined_player_data.append({
            "PlayerName": batting_player["StrikerName"],
            "ClientPlayerID": batting_player["ClientPlayerID"],
            "Points": total_points
        })
        existing_client_ids.add(batting_player["ClientPlayerID"])
    
    
for bowling_player in json_data_bowler["mostwickets"]:
    # Find matching player in the bowling data
    batting_player = next(
        (player for player in json_data_scorer["toprunsscorers"]
         if player["ClientPlayerID"] == bowling_player["ClientPlayerID"]),
        None
    )

    # Calculate total points
    if batting_player:
        total_points = batting_player["Points"] + bowling_player["Points"]
    else:
        total_points = bowling_player["Points"]

    # Create combined player data
    if bowling_player["ClientPlayerID"] not in existing_client_ids:
        # Create combined player data
        combined_player_data.append({
            "PlayerName": bowling_player["BowlerName"],
            "ClientPlayerID": bowling_player["ClientPlayerID"],
            "Points": total_points
        })
        existing_client_ids.add(bowling_player["ClientPlayerID"])
    
# Create a new JSON object
final_data = {"players": combined_player_data}

with open(r"C:\Files\LearningContent\MachineLearning\IPL\players2.json", "r") as file:
    players_data = json.load(file)
print("player2 loaded")

player_dictionary = {}

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


    
for player in players_data:
    player["points"] = player_dictionary.get(player["playerName"],0)

# File name
file_name = r"C:\Files\LearningContent\MachineLearning\IPL\players4.json"

# Writing JSON data to file
with open(file_name, "w") as json_file:
    json.dump(players_data, json_file, indent=4)

print(f"Data successfully written to {file_name}")