import numpy as np
import os
import pandas as pd
import pickle

from tqdm import tqdm

def build_teammate_matrix(players, save=True):
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
    #players = pd.read_csv("./data/players.csv")
    N = players.shape[0]
    #player_id_dict = {i: str(players["playerid"][i]) for i in range(N)}

    # Read all player data files into memory
    print("Loading data files...")
    data = {} # keys are player ids, values are dataframes
    for pid in players["playerid"]:
        data[str(pid)] = pd.read_csv("./data/player/" + str(pid) + ".csv")

    # Create teammate matrix
    print("Building matrix...")
    matrix = {} #np.zeros((N, N))
    for i in tqdm(range(N)):
        # Get data for player i. We open it here for efficiency, since it can be reused
        pid1 = str(players["playerid"][i])
        df1 = data[pid1]
        p1_data = set([(df1["ateam"][k], df1["aseason"][k]) for k in range(df1.shape[0])]) # turn dataframe into set of tuples (1 tuple per row)

        for j in range(i, N):
            # If i and j are the same, just leave those entries as 0
            if i == j:
                continue

            # Get data for player j
            pid2 = str(players["playerid"][j])
            df2 = data[pid2]
            p2_data = set([(df2["ateam"][k], df2["aseason"][k]) for k in range(df2.shape[0])]) # turn dataframe into set of tuples (1 tuple per row)

            # Take intersection of player data. If the result is non-empty, these players were teammates at some point
            join = p1_data.intersection(p2_data)
            if len(join) > 0:
                matrix[pid1, pid2] = 1
                matrix[pid2, pid1] = 1

    # Pickle the teammate "matrix" and id dict so we don't have to recompute it every time
    if save:
        print("Saving teammate matrix to file.")
        with open("teammate_matrix.b", "wb") as f:
            #pickle.dump((matrix, player_id_dict), f)
            pickle.dump(matrix, f)

    return matrix #, player_id_dict

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
    #matrix = build_teammate_matrix(save=True)
    #print(matrix)
    pass
