import mip
import numpy as np
import pandas as pd
import sys

from teammate_matrix import get_teammate_matrix, build_teammate_matrix

FRANCHISE_ID = {
    "Angels": 1,
    "Astros": 21,
    "Athletics": 10,
    "Blue_Jays": 14,
    "Braves": 16,
    "Brewers": 23,
    "Cardinals": 28,
    "Cubs": 17,
    "Diamondbacks": 15,
    "Dodgers": 22,
    "Giants": 30,
    "Indians": 5,
    "Mariners": 11,
    "Marlins": 20,
    "Mets": 25,
    "Nationals": 24,
    "Orioles": 2,
    "Padres": 29,
    "Phillies": 26,
    "Pirates": 27,
    "Rangers": 13,
    "Rays": 12,
    "Red_Sox": 3,
    "Reds": 18,
    "Rockies": 19,
    "Royals": 7,
    "Tigers": 6,
    "Twins": 8,
    "White_Sox": 4,
    "Yankees": 9,
}

def compute_rotation(players, idx_to_id_dict, teammate_matrix, verbose=True):
    """
    Formulate and solve a binary integer program for the problem of finding the top 5 pitchers
        in franchise history by fWAR who were never teammates for that franchise.

    Args:
        players: DataFrame containing the players (Fangraphs IDs, WAR values) for a single franchise
        idx_to_id_dict: dictionary mapping the index of each player in the players DataFrame to his Fangraphs ID
        teammate_matrix: sparse dictionary representing teammate relationships. Keys are a pair (tuple) of players, value is 1 if they played together.
            Non-teammates (i.e. value of 0) are not represented for memory efficiency
        verbose: boolean value indicating whether to display progress output of the optimization solver

    Returns:
        solution: a list containing the result. Each element is a tuple (Fangraphs ID, fWAR)
        oofv: the Optimal Objective Function Value, which is the total WAR for that rotation
    """
    N = players.shape[0]

    # Create model
    m = mip.Model(sense=mip.MAXIMIZE, solver_name=mip.CBC)
    if not verbose: # suppress optimization progress output
        m.verbose = 0

    # Create variables
    x = [m.add_var(var_type=mip.BINARY, name='var({})'.format(i)) for i in range(N)]
    y = [[m.add_var(var_type=mip.BINARY, name='var({}-{})'.format(i, j)) for j in range(N)] for i in range(N)]

    # Create objective function
    m.objective = mip.xsum(players["WAR"][i] * x[i] for i in range(N))

    # Create first constraint: exactly 5 pitchers must be chosen
    m += mip.xsum(x[i] for i in range(N)) == 5

    # Create second constraint: no teammates allowed
    m += mip.xsum(mip.xsum(teammate_matrix.get((idx_to_id_dict[i], idx_to_id_dict[j]), 0) * y[i][j] for j in range(N)) for i in range(N)) == 0

    # Constrain y variables to be product of x_i, x_j. This is a tricky way to linearize the quadratic second constraint
    for i in range(N):
        for j in range(N):
            m += y[i][j] >= x[i] + x[j] - 1
            m += y[i][j] <= x[i]
            m += y[i][j] <= x[j]

    # Solve
    m.optimize()

    # Parse solution
    solution = []
    oofv = m.objective_value
    for i in range(N):
       if np.isclose(x[i].x, 1):
           solution.append({"id": idx_to_id_dict[i], "war": players["WAR"][i]})

    return solution, oofv


def load_players(team):
    """
    Read WAR rankings from file for the provided franchise.

    Args:
        team: string containing the franchise whose data should be loaded

    Returns:
        Dictionary mapping each player ID for the franchise to their WAR total
    """
    players = pd.read_csv(f"./data/franchise/{team}.csv")[["playerid", "WAR"]]
    players["playerid"] = players["playerid"].astype("str")
    return players, {i: players["playerid"][i] for i in range(players.shape[0])}

def main():
    # Command line args
    team = sys.argv[1]

    # Load data
    players, idx_to_id_dict = load_players(team)

    # Create teammate matrix for this franchise
    teammate_matrix = build_teammate_matrix(players, FRANCHISE_ID[team], save=False)
    # for key in teammate_matrix:
    #     if "60" == key[0]:
    #         print(key, teammate_matrix[key])
    # quit()

    # Create and solve optimization problem
    solution, oofv = compute_rotation(players, idx_to_id_dict, teammate_matrix)



if __name__ == "__main__":
    main()
