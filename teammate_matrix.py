import numpy as np
import pandas as pd
import pickle

def build_teammate_matrix(save=False):
    players = pd.read_csv("./data/players.csv")
    N = players.shape[0]

    # Read all player data files into memory
    print("Loading data files...")
    data = {} # keys are player ids, values are dataframes
    for pid in players["playerid"]:
        data[str(pid)] = pd.read_csv("./data/player/" + str(pid) + ".csv")

    # Create teammate matrix
    print("Building matrix...")
    matrix = np.zeros((N, N))
    for i in range(N):
        # Get data for player i. We open it here for efficiency, since it can be reused
        df1 = data[str(players["playerid"][i])]
        p1_data = set([(df1["ateam"][k], df1["aseason"][k]) for k in range(df1.shape[0])])

        for j in range(i, N):
            print(i, j)
            # If i and j are the same, just leave those entries as 0
            if i == j:
                continue

            # Get data for player j
            df2 = data[str(players["playerid"][j])]
            p2_data = set([(df2["ateam"][k], df2["aseason"][k]) for k in range(df2.shape[0])])

            # Take intersection of player data. If the result is non-empty, these players were teammates at some point
            join = p1_data.intersection(p2_data)
            if len(join) > 0:
                matrix[i][j] = 1
                matrix[j][i] = 1

    # Pickle the teammate matrix so we don't have to recompute it every time
    if save:
        print("Saving teammate matrix to file.")
        with open("teammate_matrix2.b", "wb") as f:
            pickle.dump(matrix, f)

    return matrix

def load_teammate_matrix(file):
    return pickle.load(open(file, "rb"))


if __name__ == "__main__":
    matrix = build_teammate_matrix(save=True)
    print(matrix)
