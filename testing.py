import argparse as ap
import json

from bip import compute_rotation, load_players, FRANCHISE_ID
from teammate_matrix import build_teammate_matrix

def parse_args():
    """ Define command line arguments. """
    p = ap.ArgumentParser()

    # Team for which to construct the problem. By default, use all
    teams = list(FRANCHISE_ID.keys()) + ["all"]
    p.add_argument("--team", choices=teams, type=str, default="all")

    # Display optimization output
    p.add_argument("--verbose", action="store_true")

    return p.parse_args()

def validate_oofv(pred_oofv, reference):
    """
    Verify if the total WAR calculated from solving the optimization problem
        is the same as the reference total.

    Args:
        pred_oofv: the optimal objective function value from the solver (the total WAR total)
        reference: list containing the reference solution

    Returns:
        string containing the result of the validation
    """
    ref_oofv = sum(r["war"] for r in reference)
    if round(pred_oofv, 1) != ref_oofv:
        return "[WARNING] WAR totals do not match. Predicted {}, expected {}".format(round(pred_oofv, 1), ref_oofv)
    return "[COMPLETE] WAR totals match"

def validate_player_selection(prediction, reference, teammate_matrix):
    """
    Compare the players selected in the solution to the opti problem to the reference solution.

    Args:
        prediction: dictionary mapping a player ID to the WAR total. Only contains the players included in the solution
        reference: dictionary in the same structure as the prediction dictionary, but containing the reference solution
        teammate_matrix: dictionary encoding the teammate relationship. See build_teammate_matrix() for more details.
    """
    errors = []
    warnings = []

    # Check for equality first. If it holds, we can stop here.
    if prediction == reference:
        return errors, warnings

    # Check length. We should have picked the same number of players as in the reference solution
    if len(prediction) != len(reference):
        errors.append(f"[ERROR] Output length is {len(prediction)}, not {len(reference)}")

    # Check we don't have any teammates
    for i in range(len(prediction)):
        for j in range(i, len(prediction)):
            if (prediction[i]["id"], prediction[j]["id"]) in teammate_matrix:
                errors.append(f"[ERROR] Found teammates: {prediction[i]['id']} and {prediction[j]['id']}")

    # Compare results (the players selected) to reference, regardless of order
    pred_players = set([p["id"] for p in prediction])
    ref_players = set([r["id"] for r in reference])
    overlap = pred_players.intersection(ref_players)
    if not (overlap == pred_players == ref_players):
        # Find players that were predicted but shouldn't have been
        precision = []
        for p in pred_players:
            if p not in ref_players:
                precision.append(p)
        precision = ", ".join(precision)
        warnings.append(f"[WARNING] Found predicted players that were not in the reference solution: {precision}")

        # Find players who weren't predicted but should have been
        recall = []
        for p in ref_players:
            if p not in pred_players:
                recall.append(p)
        recall = ", ".join(recall)
        warnings.append(f"[WARNING] Found players in the reference solution that were not predicted: {recall}")

    return errors, warnings

def test_individual_team(team, verbose, reference):
    """
    Compare the solution for a particular team to the reference solution.

    Args:
        team: string containing the team name for which to solve
        verbose: boolean value. If True, show all output messages and solver output
        reference: dictionary containing the entire reference solution (for all teams)

    Returns:
        None
    """
    print(team)
    # Load data
    players, idx_to_id_dict = load_players(team)

    # Create teammate matrix for this franchise
    teammate_matrix = build_teammate_matrix(players, FRANCHISE_ID[team], save=False, verbose=verbose)

    # Create and solve optimization problem
    solution, oofv = compute_rotation(players, idx_to_id_dict, teammate_matrix, verbose=verbose)

    # Validate player results
    errors, warnings = validate_player_selection(solution, reference[team], teammate_matrix)

    # If everything matches up
    if len(errors) == 0 and len(warnings) == 0:
        print(f"[COMPLETE] Perfect player selection match: {team}")

    # If some constraints weren't satisfied
    if len(errors) > 0:
        for e in errors:
            print(e)

    # If some results don't match
    if len(warnings) > 0:
        for w in warnings:
            print(w)

    # Validate WAR total results
    oofv_status = validate_oofv(oofv, reference[team])
    print(oofv_status)
    print()

    return

def main():
    # Command line args
    args = parse_args()

    # Load reference solution
    with open("reference/article.json", "r") as f:
        reference = json.load(f)

    # Run test(s)
    if args.team == "all":
        for team in FRANCHISE_ID.keys():
            test_individual_team(team, args.verbose, reference)
    else:
        test_individual_team(args.team, args.verbose, reference)

if __name__ == "__main__":
    main()
