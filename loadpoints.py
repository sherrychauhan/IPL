import requests
import json
import csv

def run_script():
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

    # Combine data into a third JSON object update the path here
    combined_player_data = []
    existing_client_ids = set()
    conertjsontocsv (json_data_scorer["toprunsscorers"], "toprunsscorers.csv") 
    conertjsontocsv (json_data_bowler["mostwickets"], "mostwickets.csv") 

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
        else:
            total_points = batting_player["Points"]

        if batting_player["StrikerName"] not in existing_client_ids:
            # Create combined player data
            combined_player_data.append({
                "PlayerName": batting_player["StrikerName"],
                "ClientPlayerID": batting_player["ClientPlayerID"],
                "Points": total_points,
                "teamName" : batting_player["TeamName"]
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
        else:
            total_points = bowling_player["Points"]

        # Create combined player data
        if bowling_player["BowlerName"] not in existing_client_ids:
            # Create combined player data
            combined_player_data.append({
                "PlayerName": bowling_player["BowlerName"],
                "ClientPlayerID": bowling_player["ClientPlayerID"],
                "Points": total_points,
                "teamName" : bowling_player["TeamName"]
               
            })
            existing_client_ids.add(bowling_player["BowlerName"])
        
    # Create a new JSON object
    final_data = {"players": combined_player_data}

    with open(r"OwnerDataPlayer.json", "r") as file:
        players_data = json.load(file)
    print("player2 loaded")

    player_dictionary = {}
    player_teamName_dictionary = {}

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

        
    for player in players_data:
        player["points"] = player_dictionary.get(player["playerName"],0)
        player["role"] = player["role"] + " ("+  player["team"] + ")"
    # File name
    file_name = r"players_role.json"

    # Writing JSON data to file
    with open(file_name, "w") as json_file:
        json.dump(players_data, json_file, indent=4)

    return f"Data successfully written to {file_name}"

def conertjsontocsv(data, file_name):
    # File name for CSV
    #file_name = 'products.csv'
    
    # Writing JSON data to CSV
    with open(file_name, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=data[0].keys())  # Use keys as field names
        writer.writeheader()  # Write header row
        writer.writerows(data)  # Write data rows

run_script()