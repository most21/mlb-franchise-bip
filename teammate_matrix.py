import numpy as np
import os
import pandas as pd
import pickle

from tqdm import tqdm

def build_teammate_matrix(players, franchise_id, save=True, verbose=True):
    """
    Construct adjacency matrix for teammates. Stored as dictionary for efficiency.
    If A_ij = 1, player i and player j were teammates at one point. Else 0. We only store the entries with value 1.
    Note that because the "teammate" relationship is symmetric, we only compute the upper triangle of this matrix and fill in the lower entries simultaneously.

    Args:
        save: boolean value for whether to save the output of this function to a file

    Returns:
        Dictionary mapping tuple of every 2 players' IDs to the matrix value

    # Numpy 2d-array and dictionary mapping a player's index to his Fangraphs ID
    """
    # Load player list
    N = players.shape[0]

    # Set verbosity
    if verbose:
        range_obj = tqdm(range(N))
    else:
        range_obj = range(N)

    # Read all player data files into memory
    if verbose:
        print("Loading data files...")
    data = {} # keys are player ids, values are dataframes
    for pid in players["playerid"]:
        # Load data from file
        player_data = pd.read_csv("./data/player/" + str(pid) + ".csv")
        player_data["aseason"] = player_data["aseason"].astype("str")

        # Identify midseason trades and make season unique (e.g. 2002a, 2002b)
        season_counts = player_data["aseason"].value_counts()
        trade_seasons = season_counts[season_counts > 1]
        for year in trade_seasons.index:
            new_season_values = [str(year) + chr(i + ord("a")) for i in range(trade_seasons[year])]
            player_data.loc[player_data["aseason"] == year, "aseason"] = new_season_values

        # Save player data in dictionary
        data[str(pid)] = player_data

    # Create teammate matrix
    if verbose:
        print("Building matrix...")
    matrix = {} #np.zeros((N, N))
    for i in range_obj:
        # Get data for player i. We access it here for efficiency, since it can be reused
        pid1 = str(players["playerid"][i])
        df1 = data[pid1]
        p1_data = set([(df1["teamId"][k], df1["aseason"][k]) for k in range(df1.shape[0])]) # turn dataframe into set of tuples (1 tuple per row)

        for j in range(i, N):
            # If i and j are the same, just leave those entries as 0
            if i == j:
                continue

            # Get data for player j
            pid2 = str(players["playerid"][j])
            df2 = data[pid2]
            p2_data = set([(df2["teamId"][k], df2["aseason"][k]) for k in range(df2.shape[0])]) # turn dataframe into set of tuples (1 tuple per row)

            # Take intersection of player data. If the result is non-empty, these players were teammates at some point
            teammates = check_teammates(p1_data, p2_data, franchise_id)
            if teammates:
                matrix[pid1, pid2] = 1
                matrix[pid2, pid1] = 1

    # Pickle the teammate "matrix" and id dict so we don't have to recompute it every time
    if save:
        if verbose:
            print("Saving teammate matrix to file.")
        with open("teammate_matrix.b", "wb") as f:
            #pickle.dump((matrix, player_id_dict), f)
            pickle.dump(matrix, f)

    return matrix #, player_id_dict

def check_teammates(p1_data, p2_data, franchise_id):
    overlap = p1_data.intersection(p2_data)
    for id, _ in overlap:
        if id == franchise_id:
            return True
    return False



def load_teammate_matrix(file):
    return pickle.load(open(file, "rb"))

def get_teammate_matrix(matrix_loc=None, **kwargs):
    """
    Wrapper function that loads the teammate matrix from the provided location or creates a new one if necessary.

    Args:
        matrix_loc: path to the existing pickled matrix file. If None or invalid path, a new file will be created and saved.

    Returns:
        Dictionary mapping tuple of every 2 players' IDs to the matrix value

        #Numpy 2d-array and dictionary mapping a player's index to his Fangraphs ID
    """
    if matrix_loc is not None and os.path.exists(matrix_loc):
        print(f"Loading teammate matrix from {matrix_loc}")
        return load_teammate_matrix(matrix_loc)
    else:
        print("Creating teammate matrix from scratch")
        return build_teammate_matrix(**kwargs)

if __name__ == "__main__":
    players = pd.read_csv("./data/franchise/Marlins.csv")
    matrix = build_teammate_matrix(players, 20, save=False, verbose=False)
    pass
