import json
import os
import pandas as pd
import requests
import time

# Global variable for the base API endpoint. {} denotes where we need to insert our parameter values
# We don't need to specify a value for the position parameter if we want a hitter, but we still have to include the "position=" part in the URL
FANGRAPHS_PLAYER_API = "https://cdn.fangraphs.com/api/players/stats?playerid={}&position={}&z={}"
FRANCHISES = ["Angels", "Astros", "Athletics", "Blue_Jays", "Braves", "Brewers", "Cardinals", "Cubs", "Diamondbacks", "Dodgers", "Giants", "Indians", "Mariners", "Marlins", "Mets", "Nationals", "Orioles", "Padres", "Phillies", "Pirates", "Rangers", "Rays", "Red_Sox", "Reds", "Rockies", "Royals", "Tigers", "Twins", "White_Sox", "Yankees"]

def scrape_player(pid, position="P", save_path="./data/player/", save=False):
    """
    Scrape Fangraphs data for a single player.

    Args:
        pid: string containing the Fangraphs ID for the player
        position: string containing the player's primary position. Default is P
        save_path: the save path (and filename) for the output dataframe. Ignored if save=False
        save: boolean value for whether to save the output of this function to a file

    Returns:
        The scraped Fangraphs data for the player.
    """
    # Hit the Fangraphs API
    z = time.time()
    req = requests.get(FANGRAPHS_PLAYER_API.format(pid, position, z))
    res = json.loads(req.content)

    # Store season data in a Pandas dataframe instead of a JSON object
    data = pd.DataFrame(data=res["data"])

    # Drop non-MLB rows and average rows for seasons split amongst multiple teams
    data = data.loc[(data["type"] >= 0) & (data["type"] <= 5)] # highly unlikely a player spends time with more than 5 teams in a single season
    data = data.loc[data["ateam"] != "- - -"]

    # Take only the year and team name columns
    data = data[["teamId", "ateam", "aseason"]]

    # Save data to file
    if save:
        data.to_csv(save_path + str(pid) + ".csv", index=False)

    return data

def create_players_list(data_dir="./data/franchise/", save=True, save_path="./data/players.csv"):
    """
    Extract player data from each franchise data file.

    Args:
        data_dir: path to the folder containing the franchise data files
        save: boolean value for whether to save the output of this function to a file
        save_path: the save path (and filename) for the output dataframe. Ignored if save=False

    Returns:
        Dataframe containing names and Fangraphs IDs of each player contained in the franchise data.
    """
    output = pd.DataFrame(columns=["playerid", "Name"]) # empty dataframe to be populated

    # For each franchise, extract each player's name and Fangraphs ID
    for name in FRANCHISES:
        df = pd.read_csv(data_dir + name + ".csv")
        output = output.append(df[["playerid", "Name"]])
    output.drop_duplicates(inplace=True)
    output.reset_index(drop=True, inplace=True)

    # Save result to file so we don't have to repeatedly run this function
    if save:
        output.to_csv(save_path, index=False)
        print(f"Player list saved to {save_path}")

    return output

def get_players(player_loc=None, **kwargs):
    """
    Wrapper function that loads a player list from the provided location or creates a new one if necessary.

    Args:
        player_loc: path to the existing player file. If None or invalid path, a new file will be created and saved.

    Returns:
        Dataframe containing all players in the franchise data
    """
    if player_loc is not None and os.path.exists(player_loc):
        print(f"Loading player list from {player_loc}")
        return pd.read_csv(player_loc)
    else:
        print("Creating player list from scratch")
        return create_players_list(**kwargs)

def main():
    players = get_players(player_loc="./data/players.csv")
    for i, pid in enumerate(players["playerid"], start=1):
        if os.path.exists(f"./data/player/{pid}.csv"):
            print(f"{i}/{len(players)} Skipping {pid}")
            continue
        print(f"{i}/{len(players)} Scraping {pid}")
        scrape_player(pid, save=True)
        time.sleep(3)

if __name__ == "__main__": main()
