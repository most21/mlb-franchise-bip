import numpy as np
import pandas as pd
import pickle

from tqdm import tqdm

def build_teammate_matrix(save=False):
    """
    Construct adjacency matrix for teammates.
    If A_ij = 1, player i and player j were teammates at one point. Else 0.
    Note that because the "teammate" relationship is symmetric, we only compute the upper triangle of this matrix and fill in the lower entries simultaneously.

    Args:
        save: boolean value for whether to save the output of this function to a file

    Returns:
        Numpy 2d-array and dictionary mapping a player's index to his Fangraphs ID
    """
    # Load player list
    players = pd.read_csv("./data/players.csv")
    N = players.shape[0]
    player_id_dict = {i: str(players["playerid"][i]) for i in range(N)}

    # Read all player data files into memory
    print("Loading data files...")
    data = {} # keys are player ids, values are dataframes
    for pid in players["playerid"]:
        data[str(pid)] = pd.read_csv("./data/player/" + str(pid) + ".csv")

    # Create teammate matrix
    print("Building matrix...")
    matrix = np.zeros((N, N))
    for i in tqdm(range(N)):
        # Get data for player i. We open it here for efficiency, since it can be reused
        df1 = data[str(players["playerid"][i])]
        p1_data = set([(df1["ateam"][k], df1["aseason"][k]) for k in range(df1.shape[0])]) # turn dataframe into set of tuples (1 tuple per row)

        for j in range(i, N):
            # If i and j are the same, just leave those entries as 0
            if i == j:
                continue

            # Get data for player j
            df2 = data[str(players["playerid"][j])]
            p2_data = set([(df2["ateam"][k], df2["aseason"][k]) for k in range(df2.shape[0])]) # turn dataframe into set of tuples (1 tuple per row)

            # Take intersection of player data. If the result is non-empty, these players were teammates at some point
            join = p1_data.intersection(p2_data)
            if len(join) > 0:
                matrix[i][j] = 1
                matrix[j][i] = 1

    # Pickle the teammate matrix and id dict so we don't have to recompute it every time
    if save:
        print("Saving teammate matrix to file.")
        with open("teammate_matrix.b", "wb") as f:
            pickle.dump((matrix, player_id_dict), f)

    return matrix, player_id_dict

def load_teammate_matrix(file):
    return pickle.load(open(file, "rb"))


if __name__ == "__main__":
    #matrix, player_id_dict = build_teammate_matrix(save=True)
    #print(matrix)
    matrix, player_id_dict = load_teammate_matrix("teammate_matrix.b")
    print(matrix)
    print(player_id_dict)
