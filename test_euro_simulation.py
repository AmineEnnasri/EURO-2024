# test_euro_simulation.py
import pytest
from euro import simulate_match, simulate_playoff_match, simulate_draw, simulate_group_schedule, simulate_group_stage, calculate_points_and_ranking, get_best_third, gagnant, perdant

def test_simulate_match():
    # Teste la fonction simulate_match avec des équipes fictives
    team1 = {"fifa_ranking": 10}
    team2 = {"fifa_ranking": 20}
    goals_team1, goals_team2 = simulate_match(team1, team2)
    assert isinstance(goals_team1, int)
    assert isinstance(goals_team2, int)


def test_simulate_playoff_match():
    # Teste la fonction simulate_playoff_match avec des équipes fictives
    team1 = {"fifa_ranking": 15}
    team2 = {"fifa_ranking": 25}
    goals = simulate_playoff_match(team1, team2)
    assert isinstance(goals, int)

def test_simulate_draw():
    # Teste la fonction simulate_draw avec des équipes fictives
    qualified_teams = {"A": "TeamA", "B": "TeamB", "C": "TeamC", "D": "TeamD"}
    groups = simulate_draw(qualified_teams)
    assert isinstance(groups, dict)


def test_calculate_points_and_ranking():
    # Teste la fonction calculate_points_and_ranking avec des résultats fictifs
    results = {"A": [(("TeamA1", "TeamA2"), (2, 1)), (("TeamA1", "TeamA3"), (0, 1)), (("TeamA2", "TeamA3"), (1, 1))],
               "B": [(("TeamB1", "TeamB2"), (3, 0)), (("TeamB1", "TeamB3"), (1, 2)), (("TeamB2", "TeamB3"), (0, 0))]}
    standings = calculate_points_and_ranking(results)
    assert isinstance(standings, dict)

def test_get_best_third():
    # Teste la fonction get_best_third avec des classements fictifs
    standings = {"A": {"points": {"TeamA1": 6, "TeamA2": 3, "TeamA3": 1}},
                 "B": {"points": {"TeamB1": 9, "TeamB2": 4, "TeamB3": 1}}}
    best_thirds = get_best_third(standings)
    assert isinstance(best_thirds, list)

def test_gagnant():
    # Teste la fonction gagnant avec un résultat fictif
    results = {"1": (["TeamA", "TeamB"], (2, 1))}
    winner = gagnant(results, "1")
    assert isinstance(winner, tuple)

def test_perdant():
    # Teste la fonction perdant avec un résultat fictif
    results = {"1": (["TeamA", "TeamB"], (2, 1))}
    loser = perdant(results, "1")
    assert isinstance(loser, tuple)
